from helpers import table_test
import gtirb
import pytest


@pytest.mark.commit
@table_test("movzx RAX, byte ptr [EBX]", gtirb.Module.ISA.X64)
def test_sink_zero_extend(result):
    """Test that zero extend gets type sinked correctly"""
    result.assertContains("typesink", (0x4000, "DEST", "uint", "zero extends"))


@pytest.mark.commit
@table_test("movsx RAX, byte ptr [EBX]", gtirb.Module.ISA.X64)
def test_sink_sign_extend(result):
    """Test that zero extend gets type sinked correctly"""
    result.assertContains("typesink", (0x4000, "DEST", "int", "sign extends"))


@pytest.mark.commit
@table_test("xor RAX, RBX", gtirb.Module.ISA.X64)
def test_sink_logic_operation_1(result):
    """Test that bitwise-XOR gets type sinked correctly"""
    result.assertContains("typesink", (0x4000, "DEST", "uint", "typesink op"))
    result.assertContains("typesink", (0x4000, "SRC", "uint", "typesink op"))


@pytest.mark.commit
@table_test("and RAX, RBX", gtirb.Module.ISA.X64)
def test_sink_logic_operation_2(result):
    """Test that bitwise AND gets type sinked correctly"""
    result.assertContains("typesink", (0x4000, "DEST", "uint", "typesink op"))
    result.assertContains("typesink", (0x4000, "SRC", "uint", "typesink op"))


@pytest.mark.commit
@table_test("or RAX, RBX", gtirb.Module.ISA.X64)
def test_sink_logic_operation_3(result):
    """Test that bitwise OR gets type sinked correctly"""
    result.assertContains("typesink", (0x4000, "DEST", "uint", "typesink op"))
    result.assertContains("typesink", (0x4000, "SRC", "uint", "typesink op"))


@pytest.mark.commit
@table_test("xor RAX, RAX", gtirb.Module.ISA.X64)
def test_sink_logic_operation_4(result):
    """Test that XOR zero-idiom gets type sinked correctly"""
    result.assertNotContains("typesink", (0x4000, None, None, None))


@pytest.mark.commit
@table_test("add RAX, RBX", gtirb.Module.ISA.X64)
def test_sink_artihmetic_operation_1(result):
    """Test that addition gets type sinked correctly"""
    result.assertContains("typesink", (0x4000, "DEST", "int", "typesink op"))
    result.assertContains("typesink", (0x4000, "SRC", "int", "typesink op"))


@pytest.mark.commit
@table_test("sub RAX, RBX", gtirb.Module.ISA.X64)
def test_sink_artihmetic_operation_2(result):
    """Test that subtract gets type sinked correctly"""
    result.assertContains("typesink", (0x4000, "DEST", "int", "typesink op"))
    result.assertContains("typesink", (0x4000, "SRC", "int", "typesink op"))


@pytest.mark.commit
@table_test(
    """
    mov RAX, RDI
    imul RAX, RSI
    """,
    gtirb.Module.ISA.X64,
)
def test_sink_artihmetic_operation_3(result):
    """Test that signed multiply gets type sinked correctly"""
    result.assertContains("typesink", (0x4003, "DEST", "int", "typesink op"))
    result.assertContains("typesink", (0x4003, "SRC", "int", "typesink op"))


@pytest.mark.commit
@table_test(
    """
    cmp RAX, RBX
    jge x
    x:
    ret
    """,
    gtirb.Module.ISA.X64,
)
def test_sink_sign_compare_jump(result):
    """Test that compare/signed jump idioms gets type sinked correctly"""
    result.assertContains("typesink", (0x4000, "SRC", "int", "does JGE"))


@pytest.mark.commit
@table_test(
    """
    cmp RAX, RBX
    jae x
    x:
    ret
    """,
    gtirb.Module.ISA.X64,
)
def test_sink_unsigned_compare_jump(result):
    """Test that compare/unsigned jump idioms gets type sinked correctly"""
    result.assertContains("typesink", (0x4000, "SRC", "uint", "does JAE"))


@pytest.mark.commit
@table_test(
    """
    cmp EDI,6
    setb AL
    """,
    gtirb.Module.ISA.X64,
)
def test_sink_unsigned_flag_set(result):
    """Test that compare/unsigned jump idioms gets type sinked correctly"""
    result.assertContains("typesink", (0x4000, "SRC", "uint", "does SETB"))
