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

from retypd.c_types import (
    CompoundType,
    CharType,
    CType,
    FunctionType,
    IntType,
    PointerType,
    VoidType,
)
from typing import Set, Tuple


def is_type_equivalent(
    lhs: CType, rhs: CType, checked: Set[Tuple[CType, CType]]
) -> Tuple[bool, str]:
    """Compares two Retypd CType objects
    :param lhs: Left hand side type object
    :param rhs: Right hand side type object
    :param checked: Pairs of types already checked
    :returns: (valid, msg) pair, valid is True if they're equivalent and false
        otherwise. msg contains a recursively constructed message about why
        it was considered not-equal
    """
    if type(lhs) != type(rhs):
        return False, "Mismatching basic types"

    if (lhs, rhs) in checked or (rhs, lhs) in checked:
        return True, ""

    checked = checked | {(lhs, rhs)}

    if isinstance(lhs, PointerType):
        valid, msg = is_type_equivalent(
            lhs.target_type, rhs.target_type, checked
        )
        return valid, f"Pointed types differ: {msg}"
    elif isinstance(lhs, IntType):
        return (
            lhs.signed == rhs.signed and lhs.width == rhs.width,
            "Int types differ",
        )
    elif isinstance(lhs, CharType):
        return lhs.width == rhs.width, "Char types differ"
    elif isinstance(lhs, CompoundType):
        if len(lhs.fields) != len(rhs.fields):
            return (
                False,
                (
                    f"Field counts differ {len(lhs.fields)} vs. "
                    f"{len(rhs.fields)}"
                ),
            )

        for lhs_field, rhs_field in zip(lhs.fields, rhs.fields):
            if lhs_field.offset != rhs_field.offset:
                return (
                    False,
                    (
                        f"Field offsets differ: {lhs_field.offset} vs. "
                        f"{rhs_field.offset}"
                    ),
                )

            valid, msg = is_type_equivalent(
                lhs_field.ctype, rhs_field.ctype, checked
            )

            if not valid:
                return False, f"Field types differ: {msg}"
    elif isinstance(lhs, FunctionType):
        valid, msg = is_type_equivalent(
            lhs.return_type, rhs.return_type, checked
        )

        if not valid:
            return False, f"Return types differ: {msg}"

        if len(lhs.params) != len(rhs.params):
            return False, "Parameter counts differ"

        for lhs_param, rhs_param in zip(lhs.params, rhs.params):
            valid, msg = is_type_equivalent(lhs_param, rhs_param, checked)

            if not valid:
                return False, f"Parameter types differ: {msg}"
    elif isinstance(lhs, VoidType):
        pass
    else:
        raise NotImplementedError()

    return True, ""
