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

from __future__ import annotations
from ddisasm_retypd.ddisasm import get_arch_sizes
from enum import Enum
from gtirb_functions import Function
from gtirb_types import (
    GtirbTypes,
    AbstractType,
    ArrayType,
    BoolType,
    CharType,
    FunctionType,
    FloatType,
    IntType,
    PointerType,
    StructType,
    UnknownType,
    VoidType,
)
from pathlib import Path
from retypd import c_types
from retypd.clattice import CLattice, CLatticeCTypes
from retypd.schema import (
    ConstraintSet,
    DerefLabel,
    DerivedTypeVariable,
    Lattice,
    LatticeCTypes,
    LoadLabel,
    InLabel,
    OutLabel,
    StoreLabel,
    SubtypeConstraint,
)
from typing import Dict, FrozenSet, List, Set, Tuple, Type, TypeVar
import gtirb
import logging
import uuid


_T = TypeVar("_T")


class OpaqueType(c_types.CType):
    """A special opaque Retypd CType for holding a gtirb-types UUID for a type
    with no contents - an opaque type.
    """

    def __init__(self, type_id: uuid.UUID):
        self.type_id = type_id

    @property
    def size(self) -> int:
        return 0

    def __str__(self) -> str:
        return f"OPAQUE<{self.type_id}>"


class RetypdGtirbReader:
    """Generate retypd constraints from a GTIRB Module"""

    class Side(Enum):
        """Which side of the subtype a given DTV is on"""

        LEFT = "left"
        RIGHT = "right"

        def order(
            self, original: DerivedTypeVariable, other: DerivedTypeVariable
        ) -> SubtypeConstraint:
            """Given the original DTV and the new DTV, order into a subtype
            :param original: First created DTV
            :param other: Second created DTV
            :return: Ordered subtype constraint
            """
            if self == self.LEFT:
                return SubtypeConstraint(original, other)
            else:
                return SubtypeConstraint(other, original)

        def deref_path(
            self, deref: DerivedTypeVariable
        ) -> DerivedTypeVariable:
            """Add a dereference access path label to a given DTV
            :param deref: Dereferenced DTV
            :returns: DTV with new access path label appended to it
            """
            if self == self.LEFT:
                return deref.add_suffix(LoadLabel.instance())
            else:
                return deref.add_suffix(StoreLabel.instance())

    def __init__(self, module: gtirb.Module):
        self.module = module
        self.types = GtirbTypes.build_types(module)
        self.functions = {
            func.uuid: func for func in Function.build_functions(module)
        }

        if "prototypeTable" in module.aux_data:
            self.prototypes = module.aux_data["prototypeTable"].data
        else:
            self.prototypes = {}

        self.opaque_types: Dict[uuid.UUID, DerivedTypeVariable] = {}

    @classmethod
    def from_path(cls: Type[_T], ir_path: Path) -> List[_T]:
        """Load the IR object from a specific path
        :param ir_path: Path to the IR to load
        :returns: Instantiated object with loaded IR
        """
        ir = gtirb.IR.load_protobuf(str(ir_path))
        return [cls(module) for module in ir.modules]

    def _find_type_size(self, type_: AbstractType) -> int:
        """Determine the size of an abstract type
        :param type_: Abstract type to get size of
        :returns: Size in bytes of the type
        """
        if isinstance(type_, PointerType):
            size, _ = get_arch_sizes(self.module)
            return size
        elif isinstance(
            type_, (CharType, FloatType, IntType, UnknownType, StructType)
        ):
            return type_.size
        elif isinstance(type_, VoidType):
            raise ValueError("Void does not have a size")
        else:
            # Note structures are not handled here
            raise NotImplementedError()

    def _generate_opaque_constraint(
        self,
        origin: DerivedTypeVariable,
        side: Side,
        type_id: uuid.UUID,
        output: Set[SubtypeConstraint],
    ):
        """Generate constraints and new lattice elements for a type whose
        contents are not known in gtirb-types.
        :param origin: DTV that is the source of this type
        :param side: Which side of the constraint this DTV is on
        :param type_id: UUID of the type that is opaque
        :param output: Set of constraints to write to
        """
        if type_id in self.opaque_types:
            lattice_dtv = self.opaque_types[type_id]
        else:
            lattice_dtv = DerivedTypeVariable(
                f"opaque_{len(self.opaque_types)}"
            )
            self.opaque_types[type_id] = lattice_dtv
        output.add(side.order(origin, lattice_dtv))

    def _generate_ptr_constraint(
        self,
        deref: DerivedTypeVariable,
        side: Side,
        pointer_type: PointerType,
        output: Set[SubtypeConstraint],
    ):
        """Generate constraints for a type that is a pointer
        :parma deref: DTV that is the source of this type
        :param side: Which side of the constraint is this pointer on
        :param poointer_type: The pointer type object itself
        :param output: Set of constraints to write to
        """
        pointed_to = pointer_type.pointed_to

        if not pointed_to:
            self._generate_opaque_constraint(
                deref, side, pointer_type.uuid, output
            )
            return

        if isinstance(pointed_to, StructType):
            if len(pointed_to.fields) == 0:
                self._generate_opaque_constraint(
                    deref, side, pointer_type.uuid, output
                )
                return
            for (offset, field_type) in pointed_to.fields:
                assert field_type is not None
                size = self._find_type_size(field_type)
                path = side.deref_path(deref).add_suffix(
                    DerefLabel(size, offset)
                )
                self._generate_constraint(path, side, field_type, output)
        else:
            size = self._find_type_size(pointed_to)
            path = side.deref_path(deref).add_suffix(DerefLabel(size, 0))
            self._generate_constraint(path, side, pointed_to, output)

    def _generate_constraint(
        self,
        over: DerivedTypeVariable,
        side: Side,
        type_: AbstractType,
        output: Set[SubtypeConstraint],
    ):
        """Generate a constraint for derived type variable and its ground truth
           type object derived from gtirb-types
        :param over: DTV that is being associated with a given type
        :param side: Which side of the subtype relation this DTV is on
        :param type_: The ground truth type of this DTV
        :param output: Set of constraints to write to
        """
        if isinstance(type_, IntType):
            signed = "u" if not type_.is_signed else ""
            lattice = f"{signed}int{type_.size * 8}"
            lattice_dtv = DerivedTypeVariable(lattice)
            output.add(side.order(over, lattice_dtv))
        elif isinstance(type_, FloatType):
            lattice = f"float{type_.size * 8}"
            lattice_dtv = DerivedTypeVariable(lattice)
            output.add(side.order(over, lattice_dtv))
        elif isinstance(type_, CharType):
            lattice = f'char{type_.size * 8 if type_.size != 1 else ""}'
            lattice_dtv = DerivedTypeVariable(lattice)
            output.add(side.order(over, lattice_dtv))
        elif isinstance(type_, VoidType):
            lattice_dtv = DerivedTypeVariable("void")
            output.add(side.order(over, lattice_dtv))
        elif isinstance(type_, BoolType):
            lattice_dtv = DerivedTypeVariable("bool")
            output.add(side.order(over, lattice_dtv))
        elif isinstance(type_, UnknownType):
            logging.debug(f"Skipping unknown type of size {type_.size}")
        elif isinstance(type_, (ArrayType, StructType)):
            raise ValueError("Unable to handle by-value array/structures")
        elif isinstance(type_, PointerType):
            self._generate_ptr_constraint(over, side, type_, output)
        else:
            raise NotImplementedError()

    def _generate_func_constraint(
        self,
        func_name: str,
        function_type: FunctionType,
        output: Set[SubtypeConstraint],
    ):
        """Generate constraints for a given function
        :param func_name: Name of the function to derive types for
        :param function_type: The type object of this function
        :param output: Set to write constraints to
        """
        for i, arg in enumerate(function_type.argument_types):
            if not arg:
                continue

            in_dtv = DerivedTypeVariable(func_name, [InLabel(i)])
            self._generate_constraint(in_dtv, self.Side.LEFT, arg, output)

        ret_type = function_type.return_type

        if ret_type:
            out_dtv = DerivedTypeVariable(func_name, [OutLabel.instance()])
            self._generate_constraint(
                out_dtv, self.Side.RIGHT, ret_type, output
            )

    def load_function(self, fn_uuid: uuid.UUID) -> ConstraintSet:
        """Get the constraint set for a given function
        :param fn_uuid: UUID of the function to load
        :returns: Constraint set for the function's type information
        """
        constraints: Set[SubtypeConstraint] = set()
        prototype = self.prototypes[fn_uuid]
        function_type = self.types.get_type(prototype)
        function = self.functions[fn_uuid]

        assert isinstance(function_type, FunctionType)

        self._generate_func_constraint(
            function.get_name(), function_type, constraints
        )

        return ConstraintSet(constraints)

    def load_all(self) -> Dict[str, ConstraintSet]:
        """Load constraints for all functions with them available
        :returns: Map of function name to ground truth constraints
        """
        return {
            self.functions[func].get_name(): self.load_function(func)
            for func in self.prototypes.keys()
        }

    def generate_lattices(self) -> Tuple[Lattice, LatticeCTypes]:
        """Generate Retypd lattices for the currently discovered opaque types
        :returns: Lattice for retypd and lattice for CTypes
        """
        # Add all opaque type DTVs to the C-Lattice which is normally used
        class GTIRBLattice(CLattice):
            """CLattice which supports opaque types"""

            _opaque = frozenset(self.opaque_types.values())

            def __init__(self) -> None:
                super().__init__()
                # Add edges into lattice and re-compute reverse
                for dtv in self._opaque:
                    self.graph.add_edge(dtv, self._top)
                    self.graph.add_edge(self._bottom, dtv)

                # Recompute _internal after CLattice constructor since graph
                # wont have opaque nodes and cyclic check will fail
                self._internal = self._internal | self._opaque
                self.revgraph = self.graph.reverse()

            @property
            def atomic_types(self) -> FrozenSet[DerivedTypeVariable]:
                return self._internal | self._endcaps

            @property
            def internal_types(self) -> FrozenSet[DerivedTypeVariable]:
                return self._internal

        class GTIRBLatticeCTypes(CLatticeCTypes):
            """CTypes Lattice which supports opaque types"""

            lookup = {v: k for k, v in self.opaque_types.items()}

            def atom_to_ctype(self, lower_bound, upper_bound, byte_size):
                """Override DTV -> CType to support opaque types"""
                if lower_bound in self.lookup or upper_bound in self.lookup:
                    element = (
                        self.lookup.get(lower_bound)
                        or self.lookup[upper_bound]
                    )

                    return c_types.PointerType(OpaqueType(element), byte_size)

                return super().atom_to_ctype(
                    lower_bound, upper_bound, byte_size
                )

        gtirb_lattice = GTIRBLattice()
        gtirb_lattice_ctypes = GTIRBLatticeCTypes()
        return (gtirb_lattice, gtirb_lattice_ctypes)
