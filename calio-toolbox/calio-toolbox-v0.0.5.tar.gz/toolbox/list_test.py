from toolbox.list import str2list


def test_answer():
    s = "aa bb cc dd"
    assert str2list(s) == ["aa", "bb", "cc", "dd"]

    s = "aa, bb, cc, dd"
    assert str2list(s) == ["aa", "bb", "cc", "dd"]

    s = "1. aa 2. bb 3. cc 4. dd"
    assert str2list(s) == ["aa", "bb", "cc", "dd"]

