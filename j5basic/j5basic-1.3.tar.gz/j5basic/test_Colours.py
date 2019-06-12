# -*- encoding: utf-8 -*-

from j5basic import Colours

def test_generate_colours():
    colours = Colours.get_colours(10)
    assert len(colours) == 10
    assert len(set([tuple(c) for c in colours])) == 10
    colours = Colours.get_colours(2)
    assert len(colours) == 2
    assert len(set([tuple(c) for c in colours])) == 2

