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
