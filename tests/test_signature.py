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
    result.assertContains("writes_direct_return_value", ("x", 0x4000))
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
    result.assertNotContains("writes_direct_return_value", ("x", 0x4000))

    # Reachable writes to the return register
    result.assertContains("writes_direct_return_value", ("x", 0x4009))
    result.assertContains("writes_direct_return_value", ("x", 0x4010))
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
    """Test that implicit return values are calculated correctly and that reads
    to them are detected as well
    """
    result.assertContains("writes_return_value", ("x", 0x4000))
    result.assertContains("call_graph", ("y", "x"))
    result.assertNotContains("writes_direct_return_value", ("y", None))
    result.assertContains("may_pass_implicit_return_value", ("y", "x", 0x4000))

    # XXX: ddisasm appears to parse after the call as a separate function?
    result.assertContains(
        "reads_return_value", ("z", "FUN_16401", 0x4011, "RAX")
    )
    result.assertContains("writes_direct_return_value", ("FUN_16401", 0x4011))


@pytest.mark.commit
@table_test(
    """
    x:
    mov EAX, 1
    ret

    y:
    call x
    mov ebx, eax
    add ebx, 1
    mov eax, ebx
    ret
    """,
    gtirb.Module.ISA.X64,
    functions=["x", "y"],
)
def test_return_reads_direct(result):
    """Test that return value reads are calculated correctly"""
    result.assertContains("reads_return_value", ("y", "x", 0x400B, "RAX"))


@pytest.mark.commit
@table_test(
    """
    push RCX
    mov EAX, EBX
    add RBX, RAX
    pop RCX
    ret
    """,
    gtirb.Module.ISA.X64,
)
def test_reaches_without_write(result):
    """Test that reaches_without_write computes values correctly"""
    result.assertContains(
        "reaches_without_write",
        (0x4000, "RAX"),
        (0x4000, "RBX"),
        (0x4000, "RCX"),
        (0x4001, "RBX"),
        (0x4001, "RCX"),
        (0x4003, "RCX"),
    )
    result.assertNotContains(
        "reaches_without_write",
        (0x4003, "RAX"),
        (0x4006, "RBX"),
        (0x4007, "RCX"),
    )


@pytest.mark.commit
@table_test(
    """
    x:
    mov RAX, RSI
    add RAX, RDI
    ret

    y:
    mov RSI, 0
    mov RDI, 0
    call x
    ret
    """,
    gtirb.Module.ISA.X64,
    functions=["x", "y"],
)
def test_basic_arguments(result):
    """Test that handling arguments that are directly passed between functions
    can be computed correctly
    """
    result.assertContains(
        "writes_argument_before_call",
        ("y", 0x400E, "RDI", "x", 1),
        ("y", 0x4007, "RSI", "x", 2),
    )

    result.assertContains(
        "reads_unwritten_argument",
        ("x", 0x4000, "RSI", 2),
        ("x", 0x4003, "RDI", 1),
    )


@pytest.mark.commit
@table_test(
    """
    x:
    mov RAX, RSI
    add RAX, RDI
    ret

    y:
    call x
    ret

    z:
    mov RSI, 0
    mov RDI, 0
    call y
    ret
    """,
    gtirb.Module.ISA.X64,
    functions=["x", "y", "z"],
)
def test_implicit_arguments(result):
    """Test that arguments implicitly passed between functions in regsiters are
    computed correctly
    """
    result.assertContains(
        "writes_implicit_argument",
        ("z", 0x400D, "y", "x", 0x4000, 2),
        ("z", 0x4014, "y", "x", 0x4003, 1),
    )
