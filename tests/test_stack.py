from helpers import table_test
import gtirb
import pytest


@pytest.mark.commit
@table_test(
    """
    x:
    mov EAX, EBP
    mov EDX, EAX
    ret
    """,
    gtirb.Module.ISA.X64,
    functions=["x"],
)
def test_stack_track_basic(result):
    """Test that stack pointers are tracked correctly"""
    result.assertContains("stack_pointer_tracking", (0x4000, "RAX", 0))
    result.assertContains("stack_pointer_tracking", (0x4002, "RDX", 0))
    result.assertNotContains("stack_pointer_tracking", (0x4000, "RDX", 0))


@pytest.mark.commit
@table_test(
    """
    x:
    push RBX
    push RCX
    pop RDX
    mov RAX, RSP
    ret
    """,
    gtirb.Module.ISA.X64,
    functions=["x"],
)
def test_stack_track_depth(result):
    """Test that push and pop instructions compute stack depth correctly"""
    result.assertContains("stack_pointer_tracking", (0x4000, "RSP", -8))
    result.assertContains("stack_pointer_tracking", (0x4001, "RSP", -16))
    result.assertContains("stack_pointer_tracking", (0x4002, "RSP", -8))
    result.assertContains("stack_pointer_tracking", (0x4003, "RSP", -8))
    result.assertContains("stack_pointer_tracking", (0x4003, "RAX", -8))


@pytest.mark.commit
@table_test(
    """
    x:
    mov RBP, RAX
    mov RBX, RBP
    ret
    """,
    gtirb.Module.ISA.X64,
    functions=["x"],
)
def test_stack_track_overwrite(result):
    """Test that overwritten stack variables don't propagate"""
    result.assertNotContains("stack_pointer_tracking", (0x4002, "RBP", 0))
    result.assertNotContains("stack_pointer_tracking", (0x4002, "RBX", 0))
