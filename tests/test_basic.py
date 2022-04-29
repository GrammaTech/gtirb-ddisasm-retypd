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

from ast_util import TestHeader
from ddisasm_retypd import DdisasmRetypd
from ddisasm_retypd.ddisasm_retypd import print_user_types
from pathlib import Path
from retypd.c_types import FunctionType
from types_util import is_type_equivalent

import gtirb
import pytest


def pytest_generate_tests(metafunc):
    """Find and load (IR, Header) pairs from the test directory
    :parma metafunc: Test function being analyzed
    """
    if "ir" in metafunc.fixturenames and "header" in metafunc.fixturenames:
        gtirb_dir = Path(__file__).parent / "gtirb"
        source_dir = Path(__file__).parent / "src"
        gtirbs = list(gtirb_dir.glob("*.gtirb"))

        # Load all headers in <ROOT>/src/*.h
        gtirb_headers = {
            gtirb_file: (
                source_dir / f'{gtirb_file.name.rsplit("-", maxsplit=1)[0]}.h'
            )
            for gtirb_file in gtirbs
        }

        # Assuming x64 for now
        headers = set(gtirb_headers.values())
        loaded_headers = {header: TestHeader(header, 64) for header in headers}

        # Load GTIRB corresponding to the headers
        if "level" in metafunc.fixturenames:
            gtirb_loaded = [
                pytest.param(
                    gtirb.IR.load_protobuf(str(gtirb_file)),
                    loaded_headers[header_file],
                    gtirb_file.stem.rsplit("-", maxsplit=1)[1],
                    id=gtirb_file.name,
                )
                for (gtirb_file, header_file) in gtirb_headers.items()
            ]

            metafunc.parametrize("ir,header,level", gtirb_loaded)
        else:
            gtirb_loaded = [
                pytest.param(
                    gtirb.IR.load_protobuf(str(gtirb_file)),
                    loaded_headers[header_file],
                    id=gtirb_file.name,
                )
                for (gtirb_file, header_file) in gtirb_headers.items()
            ]

            metafunc.parametrize("ir,header", gtirb_loaded)


@pytest.mark.nightly
def test_derived_constraints(ir, header, tmp_path):
    """Verify that the constraints derived from retypd are valid"""
    dr = DdisasmRetypd(ir, tmp_path)
    derived_constraints_, _ = dr._solve_constraints(tmp_path, False)
    derived_constraints = {
        str(dtv): derived_constraint
        for dtv, derived_constraint in derived_constraints_.items()
    }

    for (item, header_type) in header.namespace.items():
        if not isinstance(header_type, FunctionType):
            continue

        if item not in header.derived_constraints:
            continue

        derived_constraint = derived_constraints[item]
        gt_constraint = header.derived_constraints[item]

        for constraint in gt_constraint:
            print("-------")
            print(item)
            print("Ground Truth")
            print(gt_constraint)
            print("Derived ")
            print(derived_constraint)

            assert constraint in derived_constraint.subtype, (
                f"Failed to find {constraint} in derived constraint of "
                f"function {item}"
            )


@pytest.mark.nightly
def test_correct_num_args(ir, header, tmp_path):
    """Validate that we get the number of arguments"""
    dr = DdisasmRetypd(ir, tmp_path)
    type_outs = {str(dtv): ctype for dtv, ctype in dr(compiled=False).items()}

    for (item, header_type) in header.namespace.items():
        if not isinstance(header_type, FunctionType):
            continue

        inferred_type = type_outs[item]

        cnt_inferred = len(inferred_type.params)
        cnt_header = len(header_type.params)

        assert (
            cnt_inferred == cnt_header
        ), f"Failed to get correct parameters for {item}"


@pytest.mark.nightly
def test_types_correctly(ir, header, tmp_path):
    """Validate that we are generating types correctly"""
    dr = DdisasmRetypd(ir, tmp_path)
    type_outs = {str(dtv): ctype for dtv, ctype in dr(compiled=False).items()}

    assert type_outs is not None

    missing_funcs = []
    wrong_types = []

    print("---------------")
    print_user_types(header.namespace)
    print("---------------")
    print_user_types(type_outs)
    print("---------------")

    for (item, header_type) in header.namespace.items():
        if not isinstance(header_type, FunctionType):
            continue

        if item not in type_outs:
            missing_funcs.append(item)
            continue

        inferred_type = type_outs[item]

        print(item)
        print(inferred_type.pretty_print(inferred_type.name))
        print(header_type.pretty_print(header_type.name))

        valid, msg = is_type_equivalent(inferred_type, header_type, set())
        if not valid:
            wrong_types.append((item, msg))

        print()

    if len(missing_funcs) > 0:
        raise ValueError(
            f"Missing functions in output {', '.join(missing_funcs)}"
        )

    if len(wrong_types) > 0:
        msgs = ", ".join([f"{fn}: {msg}" for (fn, msg) in wrong_types])
        raise ValueError(f"Wrong types in output {msgs}")
