from typing import Dict
from gtirb_types import (
    GtirbTypes,
    AbstractType,
    ArrayType,
    CharType,
    FunctionType,
    FloatType,
    IntType,
    PointerType,
    StructType,
    UnknownType,
    VoidType,
)
from retypd import c_types
from retypd.schema import DerivedTypeVariable

import gtirb
import uuid


class RetypdGtirbWriter:
    def __init__(self, module: gtirb.Module):
        self.module = module
        self.types = GtirbTypes(self.module)
        self.translate_cache = {}

    def _unknown_type(self, size: int) -> uuid.UUID:
        unk = UnknownType(uuid.uuid4(), self.types, size)
        self.types.map[unk.uuid] = unk
        return unk.uuid

    def _add_type(self, ctype: c_types.CType, type: AbstractType) -> uuid.UUID:
        self.types.map[type.uuid] = type
        self.translate_cache[ctype] = type.uuid
        return type.uuid

    def _translate_ctype(self, ctype: c_types.CType) -> uuid.UUID:
        if ctype is None:
            return self._unknown_type(0)

        if ctype in self.translate_cache:
            return self.translate_cache[ctype]

        if isinstance(ctype, c_types.FunctionType):
            func = FunctionType(
                uuid.uuid4(),
                self.types,
                self._translate_ctype(ctype.return_type),
                [self._translate_ctype(arg) for arg in ctype.params],
            )
            return self._add_type(ctype, func)
        elif isinstance(ctype, c_types.IntType):
            num = IntType(uuid.uuid4(), self.types, ctype.signed, ctype.width)
            return self._add_type(ctype, num)
        elif isinstance(ctype, c_types.VoidType):
            void = VoidType(uuid.uuid4(), self.types)
            return self._add_type(ctype, void)
        elif isinstance(ctype, c_types.FloatType):
            num = FloatType(uuid.uuid4(), self.types, ctype.width)
            return self._add_type(ctype, num)
        elif isinstance(ctype, c_types.CharType):
            num = CharType(uuid.uuid4(), self.types, ctype.width)
            return self._add_type(ctype, num)
        elif isinstance(ctype, c_types.ArrayType):
            array = ArrayType(
                uuid.uuid4(),
                self.types,
                self._translate_ctype(ctype.member_type),
                ctype.length,
            )
            return self._add_type(ctype, array)
        elif isinstance(ctype, c_types.PointerType):
            # Add type first then handle pointer, in case of recursive type
            ptr = PointerType(uuid.uuid4(), self.types, None,)
            tmp = self._add_type(ctype, ptr)
            ptr._pointed_to = self._translate_ctype(ctype.target_type)
            return tmp
        elif isinstance(ctype, c_types.StructType):
            struct = StructType(
                uuid.uuid4(),
                self.types,
                ctype.size if ctype.fields[-1].ctype is not None else 0,
                [
                    (field.offset or 0, self._translate_ctype(field.ctype),)
                    for field in ctype.fields
                ],
            )
            return self._add_type(ctype, struct)
        else:
            print(f"Failed to translate {type(ctype)}")
            raise NotImplementedError()

    def add_types(
        self, derived_types: Dict[DerivedTypeVariable, c_types.CType]
    ):
        for type_obj in derived_types.values():
            self._translate_ctype(type_obj)

        self.types.save()
