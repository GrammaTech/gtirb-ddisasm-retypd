from retypd.schema import DerivedTypeVariable, Lattice, LatticeCTypes
from retypd.c_types import (
    ArrayType,
    CharType,
    IntType,
    FunctionType,
    VoidType,
)
from typing import FrozenSet
import networkx


class DdisasmLattice(Lattice[DerivedTypeVariable]):
    # Actual C types
    _int = DerivedTypeVariable("int")
    _uint = DerivedTypeVariable("uint")
    _void = DerivedTypeVariable("void")
    _call = DerivedTypeVariable("call")

    _top = DerivedTypeVariable("┬")
    _bottom = DerivedTypeVariable("┴")

    _internal = frozenset({_int, _uint, _void, _call})
    _endcaps = frozenset({_top, _bottom})

    def __init__(self) -> None:
        self.graph = networkx.DiGraph()
        self.graph.add_edge(self._uint, self.top)
        self.graph.add_edge(self._int, self._uint)
        self.graph.add_edge(self._void, self.top)
        self.graph.add_edge(self._call, self._top)
        self.graph.add_edge(self._bottom, self._call)
        self.graph.add_edge(self._bottom, self._int)
        self.graph.add_edge(self._bottom, self._void)
        self.revgraph = self.graph.reverse()

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
        return networkx.lowest_common_ancestor(self.graph, t, v)

    def join(
        self, t: DerivedTypeVariable, v: DerivedTypeVariable
    ) -> DerivedTypeVariable:
        return networkx.lowest_common_ancestor(self.revgraph, t, v)


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
            DdisasmLattice._void: VoidType(),
            DdisasmLattice._call: FunctionType(VoidType(), []),
        }.get(atom, default)
