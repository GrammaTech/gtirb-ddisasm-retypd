from retypd.schema import DerivedTypeVariable, Lattice, LatticeCTypes
from retypd.c_types import (
    ArrayType,
    CharType,
    IntType,
    FunctionType,
    PointerType,
    VoidType,
)
from typing import FrozenSet


class DdisasmLattice(Lattice[DerivedTypeVariable]):
    # Actual C types
    _int = DerivedTypeVariable("int")
    _uint = DerivedTypeVariable("uint")
    _str = DerivedTypeVariable("str")
    _void = DerivedTypeVariable("void")
    _call = DerivedTypeVariable("call")

    _success = DerivedTypeVariable("#SuccessZ")
    _fd = DerivedTypeVariable("#FileDescriptor")

    _top = DerivedTypeVariable("┬")
    _bottom = DerivedTypeVariable("┴")

    _internal = frozenset({_int, _uint, _void, _str, _call, _fd, _success})
    _endcaps = frozenset({_top, _bottom})

    def __init__(self) -> None:
        pass

    @property
    def atomic_types(self) -> FrozenSet[DerivedTypeVariable]:
        return DdisasmLattice._internal | DdisasmLattice._endcaps

    @property
    def internal_types(self) -> FrozenSet[DerivedTypeVariable]:
        return DdisasmLattice._internal

    @property
    def top(self) -> DerivedTypeVariable:
        return DdisasmLattice._top

    @property
    def bottom(self) -> DerivedTypeVariable:
        return DdisasmLattice._bottom

    def meet(
        self, t: DerivedTypeVariable, v: DerivedTypeVariable
    ) -> DerivedTypeVariable:
        if t == v:
            return t
        # idempotence
        if t == DdisasmLattice._top:
            return v
        if v == DdisasmLattice._top:
            return t
        types = {t, v}
        # dominance
        if DdisasmLattice._bottom in types:
            return DdisasmLattice._bottom
        if DdisasmLattice._void in types:
            return DdisasmLattice._void

        # the two types are not equal and neither is TOP or BOTTOM, so if
        # either is STR then the two are incomparable
        if DdisasmLattice._str in types:
            return DdisasmLattice._bottom
        # the remaining cases are integral types. If one is INT, they are
        # comparable
        if DdisasmLattice._call in types:
            types -= {DdisasmLattice._call}
            return next(iter(types))
        if DdisasmLattice._uint in types:
            types -= {DdisasmLattice._uint}
            return next(iter(types))
        if DdisasmLattice._int in types:
            types -= {DdisasmLattice._int}
            return next(iter(types))
        # the only remaining case is SUCCESS and FILE_DESCRIPTOR, which are not
        # comparable
        return DdisasmLattice._bottom

    def join(
        self, t: DerivedTypeVariable, v: DerivedTypeVariable
    ) -> DerivedTypeVariable:
        if t == v:
            return t
        # idempotence, where _void acts identically to _bottom
        if t in {DdisasmLattice._bottom, DdisasmLattice._void}:
            return v
        if v in {DdisasmLattice._bottom, DdisasmLattice._void}:
            return t

        types = {t, v}

        # dominance
        if DdisasmLattice._top in types:
            return DdisasmLattice._top
        if DdisasmLattice._call in types:
            return DdisasmLattice._call

        # the two types are not equal and neither is TOP or BOTTOM, so if
        # either is STR then the two
        # are incomparable
        if DdisasmLattice._str in types:
            return DdisasmLattice._bottom
        if DdisasmLattice._uint in types:
            return DdisasmLattice._uint
        # the remaining cases are integral types. In all three combinations of
        # two, the least upper
        # bound is INT.
        return DdisasmLattice._int


class DdisasmLatticeCTypes(LatticeCTypes):
    def atom_to_ctype(self, lower_bound, upper_bound, byte_size):
        if upper_bound == DdisasmLattice._top:
            atom = lower_bound
        elif lower_bound == DdisasmLattice._bottom:
            atom = upper_bound
        else:
            atom = lower_bound

        default = ArrayType(CharType(1), byte_size)

        return {
            DdisasmLattice._int: IntType(byte_size, True),
            DdisasmLattice._uint: IntType(byte_size, False),
            DdisasmLattice._str: PointerType(CharType(1), byte_size),
            DdisasmLattice._void: VoidType(),
            DdisasmLattice._call: FunctionType(VoidType(), []),
        }.get(atom, default)
