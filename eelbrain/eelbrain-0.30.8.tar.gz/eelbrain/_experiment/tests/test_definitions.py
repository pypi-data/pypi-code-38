# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from eelbrain._experiment.definitions import find_dependent_epochs, find_epoch_vars, find_epochs_vars
from eelbrain._experiment.test_def import find_test_vars
from eelbrain._experiment.variable_def import Variables


def test_find_epoch_vars():
    assert find_epoch_vars({'sel': "myvar == 'x'"}) == {'myvar'}
    assert find_epoch_vars({'post_baseline_trigger_shift': "myvar"}) == {'myvar'}

    epochs = {'a': {'sel': "vara == 'a'"},
              'b': {'sel': "logical_and(varb == 'b', varc == 'c')"},
              'sec': {'sel_epoch': 'a', 'sel': "svar == 's'"},
              'super': {'sub_epochs': ('a', 'b')}}
    assert find_epochs_vars(epochs) == {'a': {'vara'},
                                        'b': {'logical_and', 'varb', 'varc'},
                                        'sec': {'vara', 'svar'},
                                        'super': {'vara', 'logical_and', 'varb', 'varc'}}
    assert set(find_dependent_epochs('a', epochs)) == {'sec', 'super'}
    assert find_dependent_epochs('b', epochs) == ['super']
    assert find_dependent_epochs('sec', epochs) == []
    assert find_dependent_epochs('super', epochs) == []


def test_find_test_vars():
    assert find_test_vars({'kind': 'anova', 'model': "a % b % c", 'vars': Variables(None)}) == {'a', 'b', 'c'}
    assert find_test_vars({'kind': 'two-stage', 'stage_1': "a + b + a*b", 'vars': Variables(None)}) == {'a', 'b'}
    test_def = {'kind': 'two-stage',
                'stage_1': "a + b + a*b",
                'vars': Variables(("a = c * d", "b = c * e"))}
    assert find_test_vars(test_def) == {'c', 'd', 'e'}
    test_def = {'kind': 'two-stage',
                'stage_1': "a + b + a*b",
                'vars': Variables({'a': 'c * d',
                                   'b': 'c * e',
                                   'x': 'something * nonexistent'})}
    assert find_test_vars(test_def) == {'c', 'd', 'e'}
    test_def = {'kind': 'two-stage',
                'stage_1': "a + b + a*b",
                'vars': Variables({'a': ('c%d', {}),
                                   'b': ('c%e', {})})}
    assert find_test_vars(test_def) == {'c', 'd', 'e'}
