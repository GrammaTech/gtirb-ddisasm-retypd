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

import logging
from typing import Dict
from gtirb_functions import Function
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
    """Write gtirb-type data from CType data from retypd"""

    def __init__(self, module: gtirb.Module):
        self.module = module
        self.types = GtirbTypes(self.module)
        self.translate_cache = {}

    def _unknown_type(self, size: int) -> uuid.UUID:
        """Generate a unique unknown type of a given size
        :param size: Size in bytes of the unknown type
        :returns: gtirb-type UUID of allocated type
        """
        unk = UnknownType(uuid.uuid4(), self.types, size)
        self.types.map[unk.uuid] = unk
        return unk.uuid

    def _add_type(self, ctype: c_types.CType, type: AbstractType) -> uuid.UUID:
        """Add a CType object's new gtirb-type
        :param ctype: CType object whose gtirb-type is being added
        :param type: gtirb-type object who is being added
        :returns: UUID of the new gtirb-type
        """
        self.types.map[type.uuid] = type
        self.translate_cache[ctype] = type.uuid
        return type.uuid

    def _translate_ctype(self, ctype: c_types.CType) -> uuid.UUID:
        """Translate a CType object to a gtirb-retypd object
        :param ctype: CType object to translate
        :returns: Allocated UUID for that gtirb-type object
        """
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
            ptr = PointerType(
                uuid.uuid4(),
                self.types,
                None,
            )
            tmp = self._add_type(ctype, ptr)
            ptr._pointed_to = self._translate_ctype(ctype.target_type)
            return tmp
        elif isinstance(ctype, c_types.StructType):
            struct = StructType(
                uuid.uuid4(),
                self.types,
                ctype.size if ctype.fields[-1].ctype is not None else 0,
                [
                    (
                        field.offset or 0,
                        self._translate_ctype(field.ctype),
                    )
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
        """Add all types from the output to a GTIRB module
        :param derived_types: Output CType map from retypd
        """
        functions = Function.build_functions(self.module)
        name2func = {function.names[0]: function for function in functions}
        prototypeTable = {}

        for dtv, type_obj in derived_types.items():
            type_id = self._translate_ctype(type_obj)
            func = name2func.get(str(dtv), None)

            if func is not None:
                prototypeTable[func.uuid] = type_id
            else:
                logging.warning(f"Failed to find function for {dtv}")

        self.types.save()
        self.module.aux_data["prototypeTable"] = gtirb.AuxData(
            prototypeTable, "mapping<UUID,UUID>"
        )
