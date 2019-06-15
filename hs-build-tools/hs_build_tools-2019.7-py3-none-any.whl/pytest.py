from hs_build_tools.assert_text_template import build_assert_text


def ok_(b, msg=None):
    if msg is None:
        assert b
    else:
        assert b , msg

def eq_(a, b, msg=None):
    if msg is None:
        assert a == b
    else:
        assert a == b, msg


assert_text = build_assert_text(ok_, eq_)


def doctest_for_assert_text():
    '''
    matches texts ignoring spaces.

    Some fragment of the `src` could be ignored if it is maked
    inside `expect` with placeholders:

    ... - ignore word
    .... - ignore any number of words until next word match

    TODO: it works but it is inconsistent with ellipsis syntax in
    doctest. I guess you could see bit of irony bellow.

    >>> assert_text('abc   xyz', ' abc xyz ')
    >>> assert_text('abc asdf  xyz', ' abc ... xyz ')
    >>> assert_text('abc asdf iklmn xyz', ' abc ... xyz ')
    Traceback (most recent call last):
    ...
    AssertionError
    >>> assert_text('abc asdf iklmn xyz', ' abc .... xyz ')
    >>> save_vars = []
    >>> pattern = ' abc ... rrr ... xyz '
    >>> assert_text('abc asdf rrr qqq xyz', pattern, save_vars)
    >>> save_vars
    ['asdf', 'qqq']

    '''
    ...
