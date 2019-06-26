from eelbrain._text import enumeration


def test_text():
    "Test _report text functions"
    assert enumeration(['a', 'b', 'c']) == 'a, b and c'
    print(enumeration({'a', 'b', 'c'}))
    assert enumeration(['a', 2]) == 'a and 2'
