import aiotoolz


def test_tlz():
    import aiotlz
    aiotlz.curry
    aiotlz.functoolz.curry
    assert aiotlz.__package__ == 'aiotlz'
    assert aiotlz.__name__ == 'aiotlz'
    import aiotlz.curried
    assert aiotlz.curried.__package__ == 'aiotlz.curried'
    assert aiotlz.curried.__name__ == 'aiotlz.curried'
    aiotlz.curried.curry
    import aiotlz.curried.operator
    assert aiotlz.curried.operator.__package__ in (None, 'aiotlz.curried')
    assert aiotlz.curried.operator.__name__ == 'aiotlz.curried.operator'
    assert aiotlz.functoolz.__name__ == 'aiotlz.functoolz'
    m1 = aiotlz.functoolz
    import aiotlz.functoolz as m2
    assert m1 is m2
    import aiotlz.sandbox
    try:
        import tlzthisisabadname.curried
        1/0
    except ImportError:
        pass
    try:
        import aiotlz.curry
        1/0
    except ImportError:
        pass
    try:
        import aiotlz.badsubmodulename
        1/0
    except ImportError:
        pass

    assert aiotoolz.__package__ == 'aiotoolz'
    assert aiotoolz.curried.__package__ == 'aiotoolz.curried'
    assert aiotoolz.functoolz.__name__ == 'aiotoolz.functoolz'
    try:
        import cytoolz
        assert cytoolz.__package__ == 'cytoolz'
        assert cytoolz.curried.__package__ == 'cytoolz.curried'
        assert cytoolz.functoolz.__name__ == 'cytoolz.functoolz'
    except ImportError:
        pass

    assert aiotlz.__file__ == aiotoolz.__file__
    assert aiotlz.functoolz.__file__ == aiotoolz.functoolz.__file__

    assert aiotlz.pipe is aiotoolz.pipe

    assert 'aiotlz' in aiotlz.__doc__
    assert aiotlz.curried.__doc__ is not None
