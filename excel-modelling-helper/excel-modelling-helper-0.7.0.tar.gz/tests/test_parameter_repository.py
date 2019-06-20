import unittest
from unittest import skip

from excel_helper import ParameterRepository, Parameter


class ParameterRepositoryTestCase(unittest.TestCase):

    def test_clear_cache(self):
        parameter_kwargs_def = {'tags': 't1,t2', 'unit': 'kg', 'name': 'test', 'source_scenarios_string': '', 'module_name': 'numpy.random',
                                'distribution_name': 'normal', 'param_a': 40, 'param_b': 4, 'param_c': ''}
        p = Parameter(**parameter_kwargs_def)

        repo = ParameterRepository()
        repo.add_parameter(p)

        param = repo['test']
        v = param()
        print(v)

        repo.clear_cache()

        assert param.cache == None

    def test_add_parameter(self):
        p = Parameter('test')

        repo = ParameterRepository()
        repo.add_parameter(p)

    @skip
    def test_template_add_scenario_parameter(self):
        """
        Test that missing properties are copied over from default parameter
        :return:
        """
        assert False

    def test_get_parameter_getitem(self):
        p = Parameter('test')

        repo = ParameterRepository()
        repo.add_parameter(p)

        _p = repo['test']
        assert type(p) == Parameter
        assert _p == p

    def test_get_parameter_defaultscenario(self):
        p = Parameter('test')

        repo = ParameterRepository()
        repo.add_parameter(p)

        _p = repo.get_parameter('test')
        assert type(p) == Parameter
        assert _p == p

    def test_get_parameter_scenario(self):
        p = Parameter('p', source_scenarios_string='test_scenario')
        r = Parameter('r', source_scenarios_string='test_scenario')

        repo = ParameterRepository()
        repo.add_parameter(p)
        repo.add_parameter(r)

        _p = repo.get_parameter('p', 'test_scenario')
        assert _p.name == 'p'

    def test_multiple_scenarios(self):
        p = Parameter('test', source_scenarios_string='s1,s2')

        repo = ParameterRepository()
        repo.add_parameter(p)

        _p = repo.get_parameter('test', 's1')

        assert _p == p

    def test_get_by_tag(self):
        r = Parameter('r', tags='t2')

        repo = ParameterRepository()

        repo.add_parameter(r)
        param_sets_t2 = repo.find_by_tag('t2')
        assert len(param_sets_t2[r.name]) == 1

    def test_multiple_tags(self):
        p = Parameter('test', tags='t1,t2')
        r = Parameter('r', tags='t2')

        repo = ParameterRepository()
        repo.add_parameter(p)
        repo.add_parameter(r)

        param_sets_t1 = repo.find_by_tag('t1')

        assert p.name in param_sets_t1.keys()
        assert len(param_sets_t1[p.name]) == 1
        assert param_sets_t1[p.name].pop().name == p.name

        param_sets_t2 = repo.find_by_tag('t2')
        assert len(param_sets_t2) == 2

    def test_exists(self):
        p = Parameter('test')

        repo = ParameterRepository()
        repo.add_parameter(p)

        assert repo.exists('test')

    def test_exists_with_scenario(self):
        p = Parameter('test', source_scenarios_string='test_scenario')

        repo = ParameterRepository()
        repo.add_parameter(p)

        assert repo.exists('test', scenario='test_scenario')
        _p = repo.get_parameter('test', 'test_scenario')
        assert _p.name == 'test'

    def test_exists_without_scenario_not_exists(self):
        p = Parameter('test')

        repo = ParameterRepository()
        repo.add_parameter(p)

        assert not repo.exists('test', scenario='test_scenario')

    def test_exists_with_scenario_not_exists(self):
        p = Parameter('test', source_scenarios_string='test_scenario')

        repo = ParameterRepository()
        repo.add_parameter(p)

        assert not repo.exists('test')
        # _p = repo.get_parameter('test', 'test_scenario')
        # assert _p.name == 'test'

    def test_list_scenarios(self):
        p = Parameter('test', source_scenarios_string='test_scenario')

        repo = ParameterRepository()
        repo.add_parameter(p)

        _p = set(repo.list_scenarios('test'))

        assert _p == set(['test_scenario'])

    def test_fill_missing_attributes_from_default_parameter(self):
        """
        Test that missing values in scenarios are being populated from the default param.
        :return:
        """
        parameter_kwargs_def = {'tags': 't1,t2', 'unit': 'kg'}

        p = Parameter('test', **parameter_kwargs_def)

        del parameter_kwargs_def['unit']
        ps = Parameter('test', source_scenarios_string='s1,s2', **parameter_kwargs_def)

        repo = ParameterRepository()
        repo.add_parameter(p)
        repo.add_parameter(ps)

        assert repo.get_parameter('test', 's1').unit == 'kg'

    def test_fill_missing_attributes_from_default_parameter_tags(self):
        """
        Test that tag values in scenarios are being overwritten with defaults.
        :return:
        """
        parameter_kwargs_def = {'tags': 't1,t2', 'unit': 'kg'}

        p = Parameter('test', **parameter_kwargs_def)

        del parameter_kwargs_def['unit']
        parameter_kwargs_def = {'tags': 't1,t3', 'unit': 'kg'}
        ps = Parameter('test', source_scenarios_string='s1,s2', **parameter_kwargs_def)

        repo = ParameterRepository()
        repo.add_parameter(p)
        repo.add_parameter(ps)

        assert repo.get_parameter('test', 's1').tags == 't1,t2'


if __name__ == '__main__':
    unittest.main()
