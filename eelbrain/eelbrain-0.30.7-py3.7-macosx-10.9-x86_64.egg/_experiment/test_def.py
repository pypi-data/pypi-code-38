# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from inspect import getfullargspec
import re

from .. import testnd
from .._exceptions import DefinitionError
from .._io.fiff import find_mne_channel_types
from .._utils.parse import find_variables
from .definitions import Definition
from .variable_def import Variables, GroupVar


__test__ = False
TAIL_REPR = {0: '=', 1: '>', -1: '<'}


def assemble_tests(test_dict):
    "Interpret dict with test definitions"
    out = {}
    for key, params in test_dict.items():
        if isinstance(params, Test):
            out[key] = params
            continue
        elif not isinstance(params, dict):
            raise TypeError(f"Invalid object for test definition {key}: {params!r}")
        params = params.copy()
        if 'stage 1' in params:
            params['stage_1'] = params.pop('stage 1')
        kind = params.pop('kind')
        if kind in TEST_CLASSES:
            out[key] = TEST_CLASSES[kind](**params)
        else:
            raise DefinitionError(f"Unknown test kind in test definition {key}: {kind}")
    return out


def tail_arg(tail):
    try:
        if tail == 0:
            return 0
        elif tail > 0:
            return 1
        else:
            return -1
    except Exception:
        raise TypeError("tail=%r; needs to be 0, -1 or 1" % (tail,))


class Test(Definition):
    "Baseclass for any test"
    kind = None
    DICT_ATTRS = ('kind', 'model', 'vars')

    def __init__(self, desc, model, vars=None):
        self.desc = desc
        self.model = model
        try:
            self.vars = Variables(vars)
        except Exception as error:
            raise DefinitionError(f"vars={vars} ({error})")

        if model is None:  # no averaging
            self._between = None
            self._within_model = None
            self._within_model_items = None
        else:
            model_elements = list(map(str.strip, model.split('%')))
            if 'group' in model_elements:
                self._between = model_elements.index('group')
                del model_elements[self._between]
            else:
                self._between = None
            self._within_model_items = model_elements
            self._within_model = '%'.join(model_elements)


class EvokedTest(Test):
    "Group level test applied to subject averages"
    def __init__(self, desc, model, cat=None, vars=None):
        Test.__init__(self, desc, model, vars)
        self.cat = cat
        if cat is not None:
            if self._within_model is None or len(self._within_model_items) == 0:
                cat = None
            elif self._between is not None:
                # remove between factor from cat
                cat = [[c for i, c in enumerate(cat) if i != self._between]
                       for cat in self.cat]
        self._within_cat = cat

    def make(self, y, ds, force_permutation, kwargs):
        raise NotImplementedError


class TTestOneSample(EvokedTest):
    """One-sample t-test

    Parameters
    ----------
    tail : int
        Tailedness of the test. ``0`` for two-tailed (default), ``1`` for upper tail
        and ``-1`` for lower tail.
    """
    kind = 'ttest_1samp'
    DICT_ATTRS = Test.DICT_ATTRS + ('tail',)

    def __init__(self, tail=0):
        desc = "%s 0" % TAIL_REPR[tail]
        EvokedTest.__init__(self, desc, '')
        self.tail = tail

    def make(self, y, ds, force_permutation, kwargs):
        return testnd.ttest_1samp(
            y, match='subject', ds=ds, tail=self.tail,
            force_permutation=force_permutation, **kwargs)


class TTest(EvokedTest):
    DICT_ATTRS = Test.DICT_ATTRS + ('c1', 'c0', 'tail')

    def __init__(self, model, c1, c0, tail, vars=None):
        tail = tail_arg(tail)
        desc = '%s %s %s' % (c1, TAIL_REPR[tail], c0)
        EvokedTest.__init__(self, desc, model, (c1, c0), vars)
        self.c1 = c1
        self.c0 = c0
        self.tail = tail


class TTestInd(TTest):
    """Independent measures t-test (comparing groups of subjects)

    Parameters
    ----------
    model : str
        The model which defines the cells that are used in the test. Usually
        ``"group"``.
    c1 : str | tuple
        The experimental group. Should be a group name.
    c0 : str | tuple
        The control group, defined like ``c1``.
    tail : int
        Tailedness of the test. ``0`` for two-tailed (default), ``1`` for upper tail
        and ``-1`` for lower tail.

    Examples
    --------
    Sample test definitions, assuming that the experiment has two groups called
    ``'younger'`` and ``'older'``::

        tests = {
            'old=young': TTestInd('group', 'older', 'younger', vars={'group': GroupVar(['younger', 'older'])}),
        }
    """
    kind = 'ttest_ind'

    def __init__(self, model, c1, c0, tail=0, vars=None):
        if vars is None and model == 'group':
            vars = (('group', GroupVar((c1, c0))),)
        TTest.__init__(self, model, c1, c0, tail, vars)

    def make(self, y, ds, force_permutation, kwargs):
        return testnd.ttest_ind(
            y, self.model, self.c1, self.c0, 'subject', ds=ds, tail=self.tail,
            force_permutation=force_permutation, **kwargs)


class TTestRel(TTest):
    """Related measures t-test

    Parameters
    ----------
    model : str
        The model which defines the cells that are used in the test. It is
        specified in the ``"x % y"`` format (like interaction definitions) where
        ``x`` and ``y`` are variables in the experiment's events.
    c1 : str | tuple
        The experimental condition. If the ``model`` is a single factor the
        condition is a :class:`str` specifying a value on that factor. If
        ``model`` is composed of several factors the cell is defined as a
        :class:`tuple` of :class:`str`, one value on each of the factors.
    c0 : str | tuple
        The control condition, defined like ``c1``.
    tail : int
        Tailedness of the test. ``0`` for two-tailed (default), ``1`` for upper tail
        and ``-1`` for lower tail.

    Examples
    --------
    Sample test definitions::

        tests = {
            'surprising=expected': TTestRel('surprise', 'surprising', 'expected'),
        }

    Notes
    -----
    For a t-test between two epochs, use an
    :class:`~eelbrain.pipeline.EpochCollection` epoch and ``model='epoch'``.
    """
    kind = 'ttest_rel'

    def __init__(self, model, c1, c0, tail=0):
        TTest.__init__(self, model, c1, c0, tail)
        assert self._between is None

    def make(self, y, ds, force_permutation, kwargs):
        return testnd.ttest_rel(
            y, self.model, self.c1, self.c0, 'subject', ds=ds, tail=self.tail,
            force_permutation=force_permutation, **kwargs)


class TContrastRel(EvokedTest):
    """Contrasts of T-maps (see :class:`eelbrain.testnd.t_contrast_rel`)

    Parameters
    ----------
    model : str
        The model which defines the cells that are used in the test. It is
        specified in the ``"x % y"`` format (like interaction definitions) where
        ``x`` and ``y`` are variables in the experiment's events.
    contrast : str
        Contrast specification using cells form the specified model (see
        :class:`eelbrain.testnd.t_contrast_rel`)).
    tail : int
        Tailedness of the test. ``0`` for two-tailed (default), ``1`` for upper tail
        and ``-1`` for lower tail.

    Examples
    --------
    Sample test definitions::

        tests = {
            'a_b_intersection': TContrastRel{'abc', 'min(a > c, b > c)', tail=1),
        }

    """
    kind = 't_contrast_rel'
    DICT_ATTRS = Test.DICT_ATTRS + ('contrast', 'tail')

    def __init__(self, model, contrast, tail=0):
        tail = tail_arg(tail)
        EvokedTest.__init__(contrast, model)
        self.contrast = contrast
        self.tail = tail

    def make(self, y, ds, force_permutation, kwargs):
        return testnd.t_contrast_rel(
            y, self.model, self.contrast, 'subject', ds=ds, tail=self.tail,
            force_permutation=force_permutation, **kwargs)


class ANOVA(EvokedTest):
    """ANOVA test

    Parameters
    ----------
    x : str
        ANOVA model specification, including ``subject`` for participant random
        effect (e.g., ``"x * y * subject"``; see :func:`eelbrain.test.anova`).
    model : str
        Model for grouping trials before averaging (by default all fixed effects
        in ``x``). Should be specified in the ``"x % y"`` format (like
        interaction definitions) where ``x`` and ``y`` are variables in the
        experiment's events.
    vars : tuple | dict
        Variables to add dynamically.

    Examples
    --------
    Sample test definitions::

        tests = {
            'one_way': ANOVA('word_type * subject'),
            'two_way': ANOVA('word_type * meaning * subject'),
        }

    """
    kind = 'anova'
    DICT_ATTRS = Test.DICT_ATTRS + ('x',)

    def __init__(self, x, model=None, vars=None):
        x = ''.join(x.split())
        if model is None:
            items = sorted(i.strip() for i in x.split('*'))
            within_items = (i for i in items if not re.match(r'^subject(\(\w+\))?$', i))
            model = '%'.join(within_items)
        EvokedTest.__init__(self, x, model, vars=vars)
        if self._between is not None:
            raise NotImplementedError("Between-subject ANOVA")
        self.x = x

    def make(self, y, ds, force_permutation, kwargs):
        return testnd.anova(y, self.x, ds=ds, force_permutation=force_permutation, **kwargs)


class TwoStageTest(Test):
    """Two-stage test: T-test of regression coefficients

    Stage 1: fit a regression model to the data for each subject.
    Stage 2: test coefficients from stage 1 against 0 across subjects.

    Parameters
    ----------
    stage_1 : str
        Stage 1 model specification. Coding for categorial predictors uses 0/1 dummy
        coding.
    vars : dict
        Add new variables for the stage 1 model. This is useful for specifying
        coding schemes based on categorial variables.
        Each entry specifies a variable with the following schema:
        ``{name: definition}``. ``definition`` can be either a string that is
        evaluated in the events-:class:`Dataset`, or a
        ``(source_name, {value: code})``-tuple (see example below).
        ``source_name`` can also be an interaction, in which case cells are joined
        with spaces (``"f1_cell f2_cell"``).
    model : str
        This parameter can be supplied to perform stage 1 tests on condition
        averages. If ``model`` is not specified, the stage1 model is fit on single
        trial data.

    Examples
    --------
    The first example assumes 2 categorical variables present in events,
    'a' with values 'a1' and 'a2', and 'b' with values 'b1' and 'b2'. These are
    recoded into 0/1 codes::

        TwoStageTest("a_num + b_num + a_num * b_num + index + a_num * index"},
                     vars={'a_num': ('a', {'a1': 0, 'a2': 1}),
                           'b_num': ('b', {'b1': 0, 'b2': 1})})

    The second test definition uses the "index" variable which is always present
    and specifies the chronological index of the events as an integer count.
    This variable can thus be used to test for a linear change over time. Due
    to the numeric nature of these variables interactions can be computed by
    multiplication::

        TwoStageTest("a_num + index + a_num * index",
                     vars={'a_num': ('a', {'a1': 0, 'a2': 1})

    Numerical variables can also defined using data-object methods (e.g.
    :meth:`Factor.label_length`) or from interactions::

        TwoStageTest('wordlength', vars={'wordlength': 'word.label_length()'})
        TwoStageTest("ab", vars={'ab': ('a%b', {'a1 b1': 0, 'a1 b2': 1, 'a2 b1': 1, 'a2 b2': 2})})
    """
    kind = 'two-stage'
    DICT_ATTRS = Test.DICT_ATTRS + ('stage_1',)

    def __init__(self, stage_1, vars=None, model=None):
        Test.__init__(self, stage_1, model, vars)
        self.stage_1 = stage_1

    def make_stage_1(self, y, ds, subject):
        """Assumes that model has already been applied"""
        return testnd.LM(y, self.stage_1, ds, subject=subject)

    def make_stage_2(self, lms, kwargs):
        lm = testnd.LMGroup(lms)
        lm.compute_column_ttests(**kwargs)
        return lm


TEST_CLASSES = {
    'anova': ANOVA,
    'ttest_1samp': TTestOneSample,
    'ttest_rel': TTestRel,
    'ttest_ind': TTestInd,
    't_contrast_rel': TContrastRel,
    'two-stage': TwoStageTest,
}
AGGREGATE_FUNCTIONS = ('mean', 'rms')
DATA_RE = re.compile(r"(source|sensor|meg|eeg)(?:\.(%s))?$" % '|'.join(AGGREGATE_FUNCTIONS))


class TestDims:
    """Data shape for test

    Paremeters
    ----------
    string : str
        String describing data.
    time : bool
        Whether the base data contains a time axis.
    morph : bool
        If loading source space data, whether the data is morphed to the common
        brain.
    """
    # eventually, specify like 'source' vs 'source time.rms'
    source = None
    sensor = None

    def __init__(self, string, time=True, morph=False):
        self.time = bool(time)
        self.morph = bool(morph)
        m = DATA_RE.match(string)
        if m is None:
            raise ValueError(f"data={string!r}: invalid test dimension description")
        dim, aggregate = m.groups()
        if dim == 'meg':
            self._to_ndvar = ('mag',)
            self.y_name = 'meg'
            dim = 'sensor'
        elif dim == 'eeg':
            self._to_ndvar = ('eeg',)
            self.y_name = 'eeg'
            dim = 'sensor'
        elif dim == 'sensor':
            self._to_ndvar = None
            self.y_name = 'meg'
        elif dim == 'source':
            self._to_ndvar = None
            self.y_name = 'srcm' if self.morph else 'src'
        else:
            raise RuntimeError(f"dim={dim!r}")
        setattr(self, dim, aggregate or True)
        if sum(map(bool, (self.source, self.sensor))) != 1:
            raise ValueError(f"data={string!r}: invalid test dimension description")
        self.string = string

        dims = []
        if self.source is True:
            dims.append('source')
        elif self.sensor is True:
            dims.append('sensor')
        if self.time is True:
            dims.append('time')
        self.dims = tuple(dims)

        # whether parc is used from subjects or from common-brain
        if self.source is True:
            self.parc_level = 'common'
        elif self.source:
            self.parc_level = 'individual'
        else:
            self.parc_level = None

    @classmethod
    def coerce(cls, obj, time=True, morph=False):
        if isinstance(obj, cls):
            if obj.time == time and obj.morph == morph:
                return obj
            else:
                return cls(obj.string, time, morph)
        else:
            return cls(obj, time, morph)

    def __repr__(self):
        return "TestDims(%r)" % (self.string,)

    def __eq__(self, other):
        if not isinstance(other, TestDims):
            return False
        return self.string == other.string and self.time == other.time

    def data_to_ndvar(self, info):
        assert self.sensor
        if self._to_ndvar is None:
            return find_mne_channel_types(info)
        else:
            return self._to_ndvar


class ROITestResult:
    """Test results for temporal tests in one or more ROIs

    Attributes
    ----------
    subjects : tuple of str
        Subjects included in the test.
    samples : int
        ``samples`` parameter used for permutation tests.
    res : {str: NDTest} dict
        Test result for each ROI.
    n_trials_ds : Dataset
        Dataset describing how many trials were used in each condition per
        subject.
    """

    def __init__(self, subjects, samples, n_trials_ds, merged_dist, res):
        self.subjects = subjects
        self.samples = samples
        self.n_trials_ds = n_trials_ds
        self.merged_dist = merged_dist
        self.res = res

    def __getstate__(self):
        return {attr: getattr(self, attr) for attr in getfullargspec(self.__init__).args[1:]}

    def __setstate__(self, state):
        self.__init__(**state)


def find_test_vars(params):
    "Find variables used in a test definition"
    if 'model' in params and params['model'] is not None:
        vs = find_variables(params['model'])
    else:
        vs = set()

    if params['kind'] == 'two-stage':
        vs.update(find_variables(params['stage_1']))

    for name, variable in params['vars'].vars.items():
        if name in vs:
            vs.remove(name)
            vs.update(variable.input_vars())
    return vs


find_test_vars.__test__ = False
