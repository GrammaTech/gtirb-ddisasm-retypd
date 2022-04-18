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
import re
import asts
import gtirb
import tempfile

from collections import defaultdict
from ddisasm_retypd import DdisasmRetypd
from pathlib import Path
from typing import List, Optional, Tuple


class UnitTestGenerator:
    """Use SEL's asts module to augment header files with their generated
    constraints for unit testing
    """

    def __init__(self, source_dir: Path, gtirb_files: List[Path]):
        self.gtirb_files = gtirb_files
        self.gtirb_headers = {
            gtirb_file: (
                source_dir / f'{gtirb_file.name.rsplit("-", maxsplit=1)[0]}.h'
            )
            for gtirb_file in gtirb_files
        }
        self.comments = defaultdict(dict)

    def _generate_comments(self, gtirb_file: Path):
        """Generate constraint comment for the functions in a given GTIRB
        :param gtirb_file: Path to the GTIRB file whose comments should be
            created
        """
        opt = gtirb_file.stem.rsplit("-", maxsplit=1)[1]

        with tempfile.TemporaryDirectory() as td_:
            td = Path(td_)
            ir = gtirb.IR.load_protobuf(str(gtirb_file))
            dr = DdisasmRetypd(ir, td)
            dr._exec_souffle(td, td)

            constraint_map = dr._insert_subtypes()

        for dtv, derived_constraint in constraint_map.items():
            comment = "\n/**\n"
            comment += f" * Generated constraints for {dtv} at -{opt}\n"
            comment += " *\n"

            # Sorting the constraints by string isn't a perfect solution, but
            # the most important functionality is to get meaningful diffs, so
            # this is a quick way to do so.
            constraints = sorted(
                [str(constraint) for constraint in derived_constraint.subtype]
            )

            for constraint in constraints:
                comment += f" * #[{opt}] {constraint}\n"
            comment += " */"
            self.comments[str(dtv)][opt] = comment

    def generate_all_comments(self):
        for gtirb_file in self.gtirb_files:
            self._generate_comments(gtirb_file)

    def _find_source_line(self, root: asts.AST, child: asts.AST) -> int:
        """Find which line of source a given child of an AST starts at
        :param"""
        for (range_child, ranges) in root.ast_source_ranges():
            if child == range_child:
                return min(ranges, key=lambda x: x[0])[0]

        raise ValueError(f"Failed to find source range for {child}")

    def _parse_comment(self, comment: str) -> Optional[Tuple[str, str]]:
        """Parse whether if a comment contains generated constraints, the name
            and version of the function that was encoded in that function
        :param comment: String of the comment being parsed
        :returns: (name, version) tuple if available, otherwise None
        """
        generated = re.findall(
            r"Generated constraints for (.*) at -(O\d)",
            comment,
        )
        return generated[0] if len(generated) > 0 else None

    def _transform_existing_comments(
        self, ast: asts.AST
    ) -> Optional[asts.LiteralOrAST]:
        """Transform comments that already exist in the AST to the new lines
        :param ast: AST to transform
        :returns: If this is a generated comment, the updated form
        """
        if isinstance(ast, asts.CComment):
            text = ast.source_text
            generated = self._parse_comment(text)

            if generated:
                name, version = generated

                if name in self.comments and version in self.comments[name]:
                    comment = self.comments[name][version]
                    del self.comments[name][version]

                    return asts.AST.from_string(
                        comment,
                        asts.ASTLanguage.C,
                        deepest=True,
                    )

    def _insert_new_comment(
        self, ast: asts.AST, name: str, version: str
    ) -> asts.AST:
        """Insert a new comment for a given tuple
        :param ast: Root AST to insert into
        :param name: Name of the function to insert for
        :param version: Version of the function to insert
        :returns: Updated AST
        """
        for child in ast.children:
            if not isinstance(child, asts.CDeclaration):
                continue

            name_ast = child.child_slot("DECLARATOR")[0].child_slot(
                "DECLARATOR"
            )

            while isinstance(
                name_ast,
                (asts.CPointerDeclarator, asts.CFunctionDeclarator0),
            ):
                name_ast = child.child_slot("TYPE")

            if isinstance(name_ast, asts.CStructSpecifier):
                continue

            assert isinstance(name_ast, asts.CIdentifier), (
                f"Failed to derive identifier for {name_ast}: "
                f"{name_ast.source_text}"
            )

            child_name = name_ast.source_text

            if child_name != name:
                continue

            comment = self.comments[name][version]
            del self.comments[name][version]

            children_line = self._find_source_line(ast, child)
            new_ast = asts.AST.from_string(
                comment,
                asts.ASTLanguage.C,
                deepest=True,
            )

            assert isinstance(new_ast, asts.CComment)
            insert_point = ast.ast_at_point(children_line - 1, 1)
            ast = asts.AST.insert(ast, insert_point, new_ast)

        return ast

    def _insert_remaining_comments(self, ast: asts.AST) -> asts.AST:
        """Insert comments that weren't used as updates of older comments into
            the root of the AST before the function declarations
        :param ast: Root AST to insert into
        :returns: The modified root AST
        """
        for name, opts in self.comments.items():
            for opt in list(opts.keys()):
                ast = self._insert_new_comment(ast, name, opt)

        return ast

    def _transform_header(self, header_file: Path, output_file: Path):
        """Run the transformation pipeline on a header file, and write the
            resultant AST back to another file
        :param header_file: Source header file
        :param output_file: Target header file
        """
        header = asts.AST.from_string(
            header_file.read_text(), asts.ASTLanguage.C
        )

        header = asts.AST.transform(header, self._transform_existing_comments)
        header = self._insert_remaining_comments(header)
        output_file.write_text(header.source_text)

    def transform_all(self, output_dir: Path):
        """Transform all loaded header files into an output directory
        :param output_dir: Directory to write resultant header files
        """
        for header_file in self.gtirb_headers.values():
            output_file = output_dir / header_file.name
            self._transform_header(header_file, output_file)


def main():
    parser = argparse.ArgumentParser(
        description="Generate unit tests for the current generated tests"
    )
    parser.add_argument("workdir", type=Path, help="Location to read from")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Location to write output to",
        required=True,
    )
    args = parser.parse_args()

    source_dir = args.workdir / "src"
    gtirb_dir = args.workdir / "gtirb"
    gtirbs = list(gtirb_dir.glob("*.gtirb"))

    gen = UnitTestGenerator(source_dir, gtirbs)
    gen.generate_all_comments()
    gen.transform_all(args.output)


if __name__ == "__main__":
    main()
