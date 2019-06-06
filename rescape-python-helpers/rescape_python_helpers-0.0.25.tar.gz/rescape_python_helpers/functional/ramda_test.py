from snapshottest import TestCase

from rescape_python_helpers.functional.ramda import to_dict_deep, all_pass_dict, flatten_dct, map_keys_deep, \
    map_with_obj_deep, pick_deep, unflatten_dct, fake_lens_path_view, key_string_to_lens_path
from . import ramda as R


def unflatten_obj(flat_dct):
    pass


class TestRamda(TestCase):

    def test_filter_dict(self):
        dct = R.filter_dict(lambda keyvalue: keyvalue[0] == 'a', dict(a=1, b=2))
        assert dct == dict(a=1)

    def test_all_pass_dict(self):
        assert all_pass_dict(lambda k, v: v, dict(a=1, b=1))
        assert not all_pass_dict(lambda k, v: v, dict(a=1, b=None))
        assert not all_pass_dict(lambda k, v: v == 2, dict(a=1, b=1))

    def test_map_prop_value_as_index(self):
        res = R.map_prop_value_as_index(
            'province',
            [
                dict(province="Alberta"),
                dict(province="Manitoba")
            ]
        )
        assert res == dict(Alberta=dict(province="Alberta"), Manitoba=dict(province="Manitoba"))

    def test_item_path_or(self):
        assert R.item_path_or('racehorse', ['one', 'one', 'was'], dict(one=dict(one=dict(was='a')))) == 'a'
        assert R.item_path_or('racehorse', ['one', 'one', 'is'], dict(one=dict(one=dict(was='a')))) == 'racehorse'
        assert R.item_path_or('racehorse', 'one.one.was', dict(one=dict(one=dict(was='a')))) == 'a'

        # Try with a mix of dict and obj
        class Fellow(object):
            def __init__(self, one):
                self.one = one

        assert R.item_path_or('racehorse', 'one.one.was', dict(one=Fellow(one=dict(was='a')))) == 'a'

    def test_omit_deep(self):
        omit_keys = ['foo', 'bar']
        dct = dict(foo=1, bar=2, car=dict(foo=3, bar=4, tar=5, pepper=[[dict(achoo=1, bar=2), dict(kale=1, foo=2)]]))
        assert R.omit_deep(omit_keys, dct) == dict(car=dict(tar=5, pepper=[[dict(achoo=1), dict(kale=1)]]))

    def test_pick_deep(self):
        pick_out = dict(billy=dict(goat=['takes', 'a', 'bite'], of=dict(tire=True, shoe={}, popsicle=None)))
        assert pick_deep(
            pick_out,
            dict(
                billy=dict(goat=['takes', 'a', 'kite'],
                           of=dict(tire=True, shoe=dict(default='left'), fruit=None, popsicle='Sweet')),
                andthe=dict(cow=['jumps', 'over', 'the', 'coon'])
            )
        ) == dict(billy=dict(goat=['takes', 'a', 'kite'], of=dict(tire=True, shoe={}, popsicle='Sweet')))

    def test_filter_deep(self):
        # This should pass
        params1 = dict(
            foo=1,
            car=dict(foo=3)
        )
        # This should fail
        params2 = dict(
            foo=1,
            car=dict(tool=3)
        )
        # This should pass
        params3 = dict(
        )
        # This should pass
        params4 = dict(
            car=dict(
                pepper=[
                    [
                        dict(achoo=1),
                        dict(kale=1)
                    ]
                ]
            )
        )
        # This should fail
        params5 = dict(
            car=dict(
                pepper=[
                    [
                        dict(achoo=1),
                        dict(kale=1),
                        dict(shoe=1)
                    ]
                ]
            )
        )

        dct = dict(
            foo=1,
            bar=2,
            car=dict(
                foo=3,
                bar=4,
                tar=5,
                pepper=[
                    [
                        dict(achoo=1, bar=2),
                        dict(kale=1, foo=2)]
                ]
            )
        )
        assert R.dict_matches_params_deep(params1, dct)
        assert not R.dict_matches_params_deep(params2, dct)
        assert R.dict_matches_params_deep(params3, dct)
        assert R.dict_matches_params_deep(params4, dct)
        assert not R.dict_matches_params_deep(params5, dct)

    def test_prop(self):
        assert R.prop('obazda', dict(obazda='dip')) == 'dip'

        # Try with a mix of dict and obj
        class Radish(object):
            def __init__(self, cut):
                self.garnish = cut

        assert R.prop('garnish', Radish('spiraled')) == 'spiraled'

    def test_merge_deep_all(self):
        assert R.merge_deep_all([
            dict(a=1, zoo=dict(a=2, b=2)),
            dict(a=2, zoo=dict(a=3, c=4, pen=dict(bull=False)), nursery=[1]),
            dict(zoo=dict(d=4, e=4, pen=dict(cow=True)), nursery=[2]),
        ]) == dict(
            a=2,
            zoo=dict(a=3, b=2, c=4, d=4, e=4, pen=dict(bull=False, cow=True)),
            nursery=[1, 2]
        )

    def test_to_dict_deep(self):
        class Beobazte(object):
            def __init__(self):
                self.cream = 'yummy'

        class Radish(object):
            def __init__(self, cut):
                self.garnish = Beobazte()
                self.cut = cut

        assert to_dict_deep(Radish('spiraled')) == dict(garnish=dict(cream='yummy'), cut='spiraled')

    def test_flatten_dct(self):
        result = flatten_dct(
            dict(iss=dict(there=dict(anybody=['willing', 'to'], listen=[dict(to='my'), 'story']))),
            '__'
        )
        assert {'iss__there__anybody__0': 'willing',
                'iss__there__anybody__1': 'to',
                'iss__there__listen__0__to': 'my',
                'iss__there__listen__1': 'story'
                } == result

    def test_unflatten_dct(self):
        dct = dict(iss=dict(there=dict(anybody=['willing', 'to'], listen=[dict(to='my'), 'story'])))
        flat_dct = flatten_dct(dct, '.')
        assert dct == unflatten_dct(flat_dct)

    def test_map_with_obj_deep(self):
        assert {
                   'a': [
                       {'b': [
                           [
                               [
                                   0,
                                   ['cCool']
                               ],
                               [
                                   1,
                                   [
                                       {'d':
                                           [
                                               'fCool'
                                           ]
                                       }
                                   ]
                               ]
                           ]
                       ]
                       }
                   ]
               } == map_with_obj_deep(
            lambda k, v: [f'{v}Cool' if isinstance(v, str) else v],
            dict(
                a=dict(
                    b=[
                        'c',
                        dict(
                            d='f'
                        )
                    ]
                )
            )
        )

    def test_map_keys_deep(self):
        assert {'aCool': {'bCool': [[0, 'c'], [1, {'dCool': 'f'}]]}} == map_keys_deep(
            lambda k, v: f'{k}Cool' if isinstance(k, str) else k,
            dict(
                a=dict(
                    b=[
                        'c',
                        dict(
                            d='f'
                        )
                    ]
                )
            )
        )

    def test_fake_lens_path_view(self):
        result = fake_lens_path_view(key_string_to_lens_path('cherry.strawberry.orange'), dict(
            cherry=dict(
                strawberry=dict(
                    orange='pretzel'
                )
            )
        ))
        assert result == 'pretzel'
