from ast_util import TestHeader
from ddisasm_retypd import DdisasmRetypd
from ddisasm_retypd.ddisasm_retypd import print_user_types
from pathlib import Path
from retypd.c_types import FunctionType
from types_util import is_type_equivalent

import gtirb
import pytest


def pytest_generate_tests(metafunc):
    """ Find and load (IR, Header) pairs from the test directory
    :parma metafunc: Test function being analyzed
    """
    if "ir" in metafunc.fixturenames and "header" in metafunc.fixturenames:
        gtirb_dir = Path(__file__).parent / "gtirb"
        source_dir = Path(__file__).parent / "src"
        gtirbs = list(gtirb_dir.glob("*.gtirb"))

        gtirb_headers = {
            gtirb_file: (
                source_dir / f'{gtirb_file.name.rsplit("-", maxsplit=1)[0]}.h'
            )
            for gtirb_file in gtirbs
        }

        headers = set(gtirb_headers.values())

        loaded_headers = {header: TestHeader(header, 64) for header in headers}

        gtirb_loaded = [
            pytest.param(
                gtirb.IR.load_protobuf(str(gtirb_file)),
                loaded_headers[header_file],
                id=gtirb_file.name,
            )
            for (gtirb_file, header_file) in gtirb_headers.items()
        ]

        metafunc.parametrize("ir,header", gtirb_loaded)


@pytest.mark.commit
def test_derived_constraints(ir, header, tmp_path):
    dr = DdisasmRetypd(ir, tmp_path)
    derived_constraints_, _ = dr._solve_constraints(tmp_path, False)
    derived_constraints = {
        str(dtv): derived_constraint
        for dtv, derived_constraint in derived_constraints_.items()
    }

    for (item, header_type) in header.namespace.items():
        if not isinstance(header_type, FunctionType):
            continue

        if item not in header.constraints:
            continue

        derived_constraint = derived_constraints[item]
        gt_constraint = header.constraints[item]

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
    """ Validate that we get the number of arguments """
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
    """ Validate that we are generating types correctly """
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
