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
def test_return_value(result):
    """Test that return values are recovered correctly"""
    result.assertContains("writes_unread_return_value", ("x", 0x4000))
