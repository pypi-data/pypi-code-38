"""Tests for the parser log line."""
from datetime import datetime

import pytest

from symbol_please.parser import LogLine

def test_parse_components():
    """Test that components are split."""
    line = LogLine("[Wed Mar 20 18:40:54 2019] Your spell fizzles!", 1)

    assert line.line_id == 1
    assert line.raw_line == "[Wed Mar 20 18:40:54 2019] Your spell fizzles!"
    assert line.raw_timestamp == "Wed Mar 20 18:40:54 2019"
    assert line.timestamp == datetime(2019, 3, 20, 18, 40, 54)
    assert line.message == "Your spell fizzles!"

def test_invalid_date():
    """Test that components are split."""
    with pytest.raises(ValueError):
        line = LogLine("[Jarbled line] Your spell fizzles!", 1)

def test_invalid_line_format():
    """Test that components are split."""
    with pytest.raises(ValueError):
        line = LogLine("Wed Mar 20 18:40:54 2019 Your spell fizzles!", 1)
