from helpers import table_test
import gtirb
import pytest


@pytest.mark.commit
@table_test(
    """
x:
    mov EAX, 1
    ret
    """,
    gtirb.Module.ISA.X64,
    functions=["x"],
)
def test_return_value_simple(result):
    """Test that return values are recovered correctly"""
    result.assertContains("writes_unread_return_value", ("x", 0x4000))
    result.assertContains("writes_return_value", ("x", 0x4000))


@pytest.mark.commit
@table_test(
    """
x:
    mov     EAX, 0
    cmp     EDI, ESI
    jle     br_true
    mov     EAX, 1
    jmp     br_done
br_true:
    mov     EAX, 2
br_done:
    ret
    """,
    gtirb.Module.ISA.X64,
    functions=["x"],
)
def test_return_value_branch(result):
    """Test that return values are recovered correctly"""
    # Unreachable write to the return register
    result.assertNotContains("writes_unread_return_value", ("x", 0x4000))

    # Reachable writes to the return register
    result.assertContains("writes_unread_return_value", ("x", 0x4009))
    result.assertContains("writes_unread_return_value", ("x", 0x4010))
    result.assertContains("writes_return_value", ("x", 0x4009))
    result.assertContains("writes_return_value", ("x", 0x4010))


@pytest.mark.commit
@table_test(
    """
x:
    mov     EAX, 1
    ret
y:
    call    x
    ret
z:
    call    y
    add     EAX, 1
    ret
    """,
    gtirb.Module.ISA.X64,
    functions=["x", "y", "z"],
)
def test_return_implicit(result):
    result.printTable("reads_implicit_return_value")
    result.assertContains("writes_return_value", ("x", 0x4000))
    result.assertContains("call_graph", ("y", "x"))
    result.assertNotContains("writes_unread_return_value", ("y", None))
    result.assertContains("may_pass_implicit_return_value", ("y", "x", 0x4000))

    # XXX: ddisasm appears to parse after the call as a separate function?
    result.assertContains(
        "reads_implicit_return_value", ("z", "FUN_16401", 0x4011, "RAX")
    )
    result.assertContains("writes_unread_return_value", ("FUN_16401", 0x4011))
