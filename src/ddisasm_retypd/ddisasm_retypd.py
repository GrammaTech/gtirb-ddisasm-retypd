# Copyright (C) 2022 GrammaTech, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# This project is sponsored by the Office of Naval Research, One
# Liberty Center, 875 N. Randolph Street, Arlington, VA 22203 under
# contract #N68335-17-C-0700.  The content of the information does not
# necessarily reflect the position or policy of the Government and no
# official endorsement should be inferred.

import argparse
from typing import Dict, List, Optional, Tuple
import gtirb
import logging
import tempfile

from ddisasm_retypd.ddisasm import (
    extract_arch_relations,
    extract_cfg_relations,
    extract_souffle_relations,
    get_arch_sizes,
    get_callgraph,
)
from ddisasm_retypd.gtirb_read import RetypdGtirbReader
from ddisasm_retypd.gtirb_write import RetypdGtirbWriter
from ddisasm_retypd.souffle import execute_souffle

from collections import defaultdict
from pathlib import Path

from retypd.clattice import CLattice, CLatticeCTypes
from retypd.c_type_generator import CTypeGenerator
from retypd.c_types import CType, FunctionType, PointerType, StructType
from retypd.solver import Sketches
from retypd.parser import SchemaParser
from retypd.schema import ConstraintSet, DerivedTypeVariable, Program
from retypd.solver import Solver, LogLevel


class DdisasmRetypd:
    DATALOG = Path(__file__).parent / "datalog" / "retypd.dl"
    # Relations to export from datalog for subtypings
    SUBTYPE_RELS = ["subtype_constraint", "comment"]

    def __init__(self, ir: gtirb.IR, facts_dir: Optional[Path] = None):
        self.ir = ir
        self.callgraph = get_callgraph(ir)
        self.facts_dir = facts_dir
        self.var_set = set()
        self.lattice = CLattice()
        self.lattice_ctypes = CLatticeCTypes()

    def _exec_souffle(
        self,
        facts_dir: Path,
        debug_dir: Optional[Path] = None,
        compiled: bool = False,
    ):
        """Execute souffle, and if available dump relations in the debug dir
        :param debug_dir: Optional directory to dump output information to
        """
        extract_souffle_relations(self.ir, facts_dir)
        extract_cfg_relations(self.ir, facts_dir)
        extract_arch_relations(self.ir, facts_dir)

        logging.info("Executing souffle")
        self._souffle_out = execute_souffle(
            facts_dir,
            self.DATALOG,
            self.SUBTYPE_RELS,
            compiled=compiled,
            debug_dir=debug_dir,
        )

    def addr_to_offset(self, loc: int) -> Optional[gtirb.Offset]:
        """Translate an address to an offset into a block
        :param loc: Address to convert to to a block
        :returns: If possible, the offset, otherwise None
        """
        module = self.ir.modules[0]
        blocks = list(module.code_blocks_on(loc))
        if len(blocks) == 1:
            block = blocks[0]
        elif len(blocks) > 1:
            logging.warning(f"Multiple blocks at {loc:08x}")
            block = blocks[0]
        else:
            logging.debug(f"No blocks at {loc:08x}")
            return None

        return gtirb.Offset(block, loc - (block.address or 0))

    def _insert_subtypes(
        self, add_comments: bool = False, debug_categories: List[str] = None
    ) -> Dict[str, ConstraintSet]:
        """Add subtypes to the constraints map
        :param add_comments: If True, a comments map will be populated with
            subtype constraints for visualization + debugging
        :param debug_categories: Which categories of relations to insert as
            comments for the output GTIRB
        :returns: Dictionary mapping function to their constraint sets and the
            variable set of known functions to analyze
        """
        constraints = self._souffle_out["subtype_constraint"]
        module = self.ir.modules[0]

        comments = defaultdict(set)

        if "comment" in self._souffle_out and debug_categories is not None:
            for (addr, comment, category) in self._souffle_out["comment"]:
                if category in debug_categories and addr != "0":
                    offset = self.addr_to_offset(int(addr))

                    if offset:
                        comments[offset].add(comment.replace("??", "s"))

        constraint_map = defaultdict(ConstraintSet)

        for (func, constraint, _) in constraints:
            try:
                constr_object = SchemaParser.parse_constraint(constraint)
            except ValueError as e:
                logging.error(f"Failed to parse {constraint}")
                raise e

            constraint_map[func].add(constr_object)

        if add_comments:
            # NOTE: This is a bit of a hack and isn't portable across
            # assemblers since it assumes the comments are denoted with hashtag
            # however for our purposes (debugging) it works.
            gtirb_comments = {
                loc: "\n# ".join(comment)
                for (loc, comment) in comments.items()
            }

            module.aux_data["comments"] = gtirb.AuxData(
                gtirb_comments, "mapping<Offset,string>"
            )

        return constraint_map

    def _solve_constraints(
        self,
        debug_dir: Optional[Path],
        compiled: bool,
        debug_categories: List[str] = None,
    ) -> Tuple[
        Dict[DerivedTypeVariable, ConstraintSet],
        Dict[DerivedTypeVariable, Sketches],
    ]:
        """Solve the current program's constraint set
        :param debug_dir: Directory to output debug information to
        :param compiled: Whether to compile the souffle program or not
        :param debug_categories: Which categories of relations to insert as
            comments for the output GTIRB
        :returns: A tuple of the mapping of the output to its derived
            constraint set, and a a mapping of the output to its sketch
        """
        if self.facts_dir:
            self._exec_souffle(self.facts_dir, debug_dir, compiled=compiled)
        else:
            with tempfile.TemporaryDirectory() as tmpdir:
                self._exec_souffle(Path(tmpdir), debug_dir, compiled=compiled)

        constraint_map = self._insert_subtypes(
            debug_dir is not None, debug_categories
        )

        # Load gtirb-type information to constraints if possible
        for module in self.ir.modules:
            reader = RetypdGtirbReader(module)
            for name, constraint_set in reader.load_all().items():
                if name in constraint_map:
                    logging.info(
                        f"Ignoring {name} generated constraints, gtirb-type "
                        "information is already populated"
                    )
                constraint_map[name] = constraint_set

            # Use new lattices with opaque types supported
            # TODO: This currently re-generates per-module, so prior modules
            # wont be taken into account. This doesn't really matter right now
            # since almost all GTIRB is 1-module, but if it ever comes up this
            # should change.
            self.lattice, self.lattice_ctypes = reader.generate_lattices()

        program = Program(self.lattice, {}, constraint_map, self.callgraph)

        logging.info("Solving constraints")
        loglevel = LogLevel.DEBUG if debug_dir else LogLevel.QUIET
        solver = Solver(program, verbose=loglevel)
        derived_constraints, sketches = solver()

        if debug_dir is not None:
            for dtv, derived_constraint in derived_constraints.items():
                logging.debug("-------")
                logging.debug(dtv)
                logging.debug("ORIGINAL")
                logging.debug(constraint_map[str(dtv)])
                logging.debug("DERIVED")
                logging.debug(derived_constraint)

            for (dtv, sketch) in sketches.items():
                out = debug_dir / f"{dtv.base}.dot"
                if len(sketch.sketches) > 0:
                    try:
                        out.write_text(sketch.to_dot(dtv))
                    except KeyError:
                        logging.warning(f"Cannot draw {dtv} sketch")

        return derived_constraints, sketches

    def __call__(
        self,
        debug_dir: Optional[Path] = None,
        compiled: bool = False,
        debug_categories: List[str] = None,
    ) -> Dict[DerivedTypeVariable, CType]:
        """Execute the retypd algorithm
        :param debug_dir: Directory to write debug output if desired
        :param compiled: Whether or not to compile the souffle program
        :param debug_categories: Which categories of relations to insert as
            comments for the output GTIRB
        :returns: Dictionary of DTV to generated C-type
        """
        addr_size, reg_size = get_arch_sizes(self.ir.modules[0])
        _, sketches = self._solve_constraints(
            debug_dir, compiled, debug_categories
        )

        gen = CTypeGenerator(
            sketches,
            self.lattice,
            self.lattice_ctypes,
            reg_size,
            addr_size,
            verbose=LogLevel.DEBUG if debug_dir else LogLevel.QUIET,
        )
        return gen()


def print_user_types(types: Dict[DerivedTypeVariable, CType]):
    """Recursively detect types that would be considered a 'user type', i.e.
        a function prototype or any compound type
    :param types: Types output by the retypd algorithm
    """
    working_types = set(types.values())
    user_defs = set()

    while len(working_types) > 0:
        type_ = working_types.pop()

        if type_ in user_defs or type_ in working_types:
            continue

        if isinstance(type_, PointerType):
            if type_.target_type is not None:
                working_types.add(type_.target_type)
        elif isinstance(type_, FunctionType):
            if type_ is not None:
                working_types.add(type_.return_type)
            for param in type_.params:
                if param is not None:
                    working_types.add(param)
        elif isinstance(type_, StructType):
            user_defs.add(type_)

            for field in type_.fields:
                working_types.add(field.ctype)

    for type_ in user_defs:
        print(type_.pretty_print(type_.name))

    for type_ in types.values():
        if hasattr(type_, "name"):
            print(type_.pretty_print(type_.name))
        else:
            print(type_.pretty_print(""))


def main():
    parser = argparse.ArgumentParser(
        description="Run retypd on ddisasm-generated GTIRB files"
    )
    parser.add_argument(
        "gtirb", type=Path, help="ddisasm generated GTIRB to operate on"
    )
    parser.add_argument("dest", type=Path, help="Path to write GTIRB to")
    parser.add_argument(
        "-d", "--debug-dir", type=Path, help="retypd constraint gen debug"
    )
    parser.add_argument(
        "--debug-category",
        action="append",
        help="Categories of relations to include as comments",
    )
    args = parser.parse_args()
    logging.getLogger().setLevel(
        logging.DEBUG if args.debug_dir is not None else logging.INFO
    )

    ir = gtirb.IR.load_protobuf(str(args.gtirb))

    logging.debug(f"Outputting relations to {args.debug_dir}")
    dr = DdisasmRetypd(ir, args.debug_dir)
    type_outs = dr(args.debug_dir, debug_categories=args.debug_category)

    if args.debug_dir is not None:
        print_user_types(type_outs)

    for module in ir.modules:
        writer = RetypdGtirbWriter(module)
        writer.add_types(type_outs)

    ir.save_protobuf(str(args.dest))


if __name__ == "__main__":
    main()
