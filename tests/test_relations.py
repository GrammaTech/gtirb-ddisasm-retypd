from helpers import table_test
import gtirb
import pytest


@pytest.mark.commit
@table_test(
    """
    mov EAX, 1
    ret
    """,
    gtirb.Module.ISA.X64,
)
def test_return_value(result):
    """Test that return values are recovered correctly"""
    result.assertContains("writes_unread_return_value", ("FUN_16384", 0x4000))
