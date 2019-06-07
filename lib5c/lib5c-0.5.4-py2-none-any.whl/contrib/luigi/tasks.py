"""
Provides luigi Task subclasses that wrap the lib5c command line functions.
"""

import time
import os
import subprocess
import uuid

import luigi

from lib5c.util.system import shell_quote

try:
    from bsub import bsub

    bsub_avail = True
except ImportError:
    bsub_avail = False


def get_all_lines(filename):
    """
    Utility function for reading all lines from a file on disk.

    Parameters
    ----------
    filename : str
        The file to read from.

    Returns
    -------
    str
        The contents of the file.
    """
    with open(filename, 'r') as handle:
        return handle.read()


def parallelize_reps(task_class, reps, **kwargs):
    """
    Parallelizes any Task class whose constructor accepts a ``rep`` kwarg across
    a list of reps by creating a new WrapperTask.

    Parameters
    ----------
    task_class : luigi.Task subclass
        The Task to parallelize.
    reps : list of str
        List of reps to parallelize over.
    kwargs : kwargs
        Additional kwargs to pass through to the Task class.

    Returns
    -------
    luigi.WrapperTask subclass
        A WrapperTask which simply requires the original ``task_class`` to be
        run for every rep in ``reps``.
    """
    return type(
        '%sWrapper_%s' % (task_class.__name__, str(uuid.uuid4())[:8]),
        (luigi.WrapperTask,),
        {'requires': lambda self: [task_class(rep=rep, **kwargs)
                                   for rep in reps]})


def parallelize_reps_regions(task_class, reps, regions, **kwargs):
    """
    Parallelizes any Task class whose constructor accepts ``rep`` and ``region``
    kwargs across lists of reps and regions by creating a new WrapperTask.

    Parameters
    ----------
    task_class : luigi.Task subclass
        The Task to parallelize.
    reps : list of str
        List of reps to parallelize over.
    regions : list of str
        List of regions to parallelize over.
    kwargs : kwargs
        Additional kwargs to pass through to the Task class.

    Returns
    -------
    luigi.WrapperTask subclass
        A WrapperTask which simply requires the original ``task_class`` to be
        run for every rep in ``reps`` and every region in ``regions``.
        """
    return type(
        '%sWrapper_%s' % (task_class.__name__, str(uuid.uuid4())[:8]),
        (luigi.WrapperTask,),
        {'requires': lambda self: [task_class(rep=rep, region=region, **kwargs)
                                   for rep in reps
                                   for region in regions]})


def add_visualization_hooks(f, pvalue=False, obs_over_exp=False, tetris=False):
    """
    Decorator intended to wrap the ``run()`` method of luigi Task subclasses to
    automatically visualize the result of the Task class after it completes.

    Parameters
    ----------
    f : function
        The function to add visualization hooks to.  Intended to be the
        ``run()`` method of luigi Task subclasses.
    pvalue : bool
        Pass True to denote that the visualized heatmaps should be drawn using
        the p-value colorscale.
    obs_over_exp : bool
        Pass True to denote that the visualized heatmaps should be drawn using
        the obs_over_exp colorscale.
    tetris : bool
        Pass True to denote that the visualized heatmaps should be drawn as
        tetris heatmaps.

    Returns
    -------
    function
        The hooked function.
    """
    def hooked(self):
        f(self)
        if self.heatmap:
            if type(self.output()) in [list, tuple]:
                if self.heatmap_outdir:
                    outfile = os.path.join(self.heatmap_outdir, '%s_%r.png')
                else:
                    outfile = os.path.join(
                        os.path.split(self.output()[0].path)[0], '%s_%r.png')
                input_paths = [i.path for i in self.output()
                               if i.path.endswith('.counts')]
                if len(input_paths) == 1:
                    infile = input_paths[0]
                    outfile = infile.replace('.counts', '_%r.png')
                else:
                    common_prefix = os.path.commonprefix(input_paths)
                    common_postfix = os.path.commonprefix(
                        [p[::-1] for p in input_paths])[::-1]
                    infile = common_prefix + '*' + common_postfix
                cmd = 'lib5c plot heatmap -p %s -R %s %s' % \
                      (self.input()[0].path, shell_quote(infile), outfile)
            else:
                if self.heatmap_outdir:
                    outfile = os.path.join(
                        self.heatmap_outdir,
                        os.path.split(self.output().path)[0].replace('.counts',
                                                                     '_%r.png'))
                else:
                    outfile = self.output().path.replace('.counts', '_%r.png')
                cmd = 'lib5c plot heatmap -p %s -R %s %s' % \
                      (self.input()[0].path, self.output().path, outfile)
            if pvalue:
                cmd += ' -P'
            elif obs_over_exp:
                cmd += ' -c obs_over_exp'
            elif tetris:
                cmd += ' -TC'
            if bsub_avail:
                job_name = '.'.join([self.__class__.__name__] +
                                    ['%s_%s' % (k, v)
                                     for k, v in self.param_kwargs.iteritems()
                                     if not hasattr(v, '__getitem__')] +
                                    ['heatmap'])
                if len(job_name) > 250:
                    job_name = '%s.%s' % (self.__class__.__name__, 'heatmap')
                sub = bsub(job_name, verbose=False)
                sub(cmd)
            else:
                print(cmd)
                subprocess.call(cmd, shell=True)

    return hooked


def visualizable(pvalue=False, obs_over_exp=False, tetris=False):
    """
    Class decorator factory for luigi Task subclasses which allows the task to
    automatically visualize itself after completion by
      1. adding ``heatmap`` and ``heatmap_outdir`` parameters to the Task and
      2. decorating the Task's ``run()`` method with
         ``add_visualization_hooks()``

    Parameters
    ----------
    pvalue : bool
        Pass True to denote that the visualized heatmaps should be drawn using
        the p-value colorscale.
    obs_over_exp : bool
        Pass True to denote that the visualized heatmaps should be drawn using
        the obs_over_exp colorscale.
    tetris : bool
        Pass True to denote that the visualized heatmaps should be drawn as
        tetris heatmaps.

    Returns
    -------
    function
        The class decorator.
    """
    def visualizable_decorator(cls):
        setattr(cls, 'heatmap', luigi.BoolParameter(default=False))
        setattr(cls, 'heatmap_outdir', luigi.Parameter(default=None))
        setattr(cls, 'run', add_visualization_hooks(
            cls.run, pvalue=pvalue, obs_over_exp=obs_over_exp, tetris=tetris))
        return cls
    return visualizable_decorator


class CmdTask(luigi.Task):
    """
    Luigi Task parent class for Tasks whose ``run()`` behavior should be to
    execute a specific command on the command line.

    Subclasses must implement ``_construct_cmd_string()``, which should return a
    string corresponding to the command to be run on the command line.

    If the ``bsub`` Python package is installed, the command will be executed
    using the bsub scheduling system, and the caller will wait for the job
    corresponding to the task to complete.

    If the ``bsub`` Python package is not installed, the command will be simply
    executed via ``subprocess``.
    """
    def _construct_cmd_string(self):
        """
        Subclasses must implement this function, see class docstring.
        """
        raise NotImplementedError()

    def run(self):
        """
        Generic ``run()`` implementation for command line Tasks.
        """
        for output in luigi.task.flatten(self.output()):
            output.makedirs()
        if bsub_avail:
            if not os.path.exists('logs'):
                os.makedirs('logs')
            job_name = '.'.join([self.__class__.__name__] +
                                ['%s_%s' % (k, v)
                                 for k, v in self.param_kwargs.iteritems()
                                 if not hasattr(v, '__getitem__')])
            if len(job_name) > 250:
                job_name = self.__class__.__name__
            sub = bsub(job_name, verbose=True)
            sub(self._construct_cmd_string())
            bsub.poll(sub.job_id)
            time.sleep(10)
            for output in luigi.task.flatten(self.output()):
                if not output.exists():
                    raise Exception(
                        'missing file: %s\nerror:\n%s\ncommand:\n%s' %
                        (output.path,
                         get_all_lines(sub.kwargs['e'].replace('%J',
                                                               sub.job_id)),
                         self._construct_cmd_string()))
        else:
            cmd = self._construct_cmd_string()
            print(cmd)
            subprocess.call(cmd, shell=True)


class RegionalTaskMixin(object):
    """
    Mixin class for Tasks that write a separate output file per region.
    """
    region = luigi.Parameter(default=None)

    def _outfile_pattern(self):
        """
        This function should return a outfile pattern that may be parameterized
        by ``_parameterized_outfile_pattern()`` and then regionalized by
        ``_regional_outfiles()``.

        Returns
        -------
        str
            The outfile pattern.
        """
        raise NotImplementedError()

    def _parameterized_outfile_pattern(self):
        """
        Plugs in parameters from this instance into the outfile pattern.

        The resulting string will be passed to the tool in the command string.

        The default implementation is to not plug in any parameters.

        Returns
        -------
        str
            The parametrized outfile pattern.
        """
        return self._outfile_pattern()

    def _regional_outfiles(self, regions=None):
        """
        Creates a list of actual expected outfiles, which can be used to
        construct the output() definition, using the outfile pattern and the
        parameters of this instance.

        For example::

            def output(self):
                return [luigi.LocalTarget(outfile)
                        for outfile in self._regional_outfiles(regions=[...])]

        Params
        ------
        regions : Optional[List[str]]
            The regions to deduce the outfiles for.

        Returns
        -------
        List[str]
            The list of actual expected outfiles.
        """
        # baseline outfile from pattern
        outfile = self._parameterized_outfile_pattern()

        # honor self.region field if present
        if self.region is not None:
            regions = [self.region]

        # parallelize across regions
        if regions is not None:
            return [outfile.replace('%r', region) for region in regions]
        else:
            return [outfile]


@visualizable()
class OutliersTask(CmdTask):
    """
    Task class for applying high outlier removal to countsfiles.

    Wraps the ``lib5c outliers`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the input countsfile
      * ``self.output()``: the resulting outlier-filtered countsfile
    """
    fold_threshold = luigi.FloatParameter(default=8.0)
    window_size = luigi.IntParameter(default=5)
    overwrite_value = luigi.Parameter(default='nan')

    def _construct_cmd_string(self):
        cmd = 'lib5c outliers -p %s -f %s -w %i -o %s' % \
              (self.input()[0].path, self.fold_threshold, self.window_size,
               self.overwrite_value)
        cmd += ' %s %s' % (self.input()[1].path, self.output().path)
        return cmd


@visualizable()
class QnormTask(CmdTask):
    """
    Task class for applying quantile normalization to countsfiles.

    Wraps the ``lib5c qnorm`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1:]``: the input countsfiles
      * ``self.output()``: not specified explicitly, see below

    Technically this class should specify a list of outputs, one for each input
    countsfile. In practice, this specification of outputs is left to whatever
    code strings together the pipeline. The ``lib5c qnorm`` command will produce
    output files on disk based on the ``outfile_pattern`` and the file names of
    the input countsfiles.
    """
    outfile_pattern = luigi.Parameter(default='qnorm/%s_qnorm.counts')
    regional = luigi.BoolParameter(default=False)
    averaging = luigi.BoolParameter(default=False)
    condition_on = luigi.Parameter(default=None)
    reference = luigi.Parameter(default=None)

    def _construct_cmd_string(self):
        cmd = 'lib5c qnorm -p %s' % self.input()[0].path
        if self.regional:
            cmd += ' -R'
        if self.averaging:
            cmd += ' -A'
        if self.condition_on is not None:
            cmd += ' -c %s' % shell_quote(self.condition_on)
        if self.reference is not None:
            cmd += ' -r %s' % shell_quote(self.reference)
        cmd += ' %s %s' % (self.outfile_pattern,
                           ' '.join(i.path for i in self.input()[1:]))
        return cmd


@visualizable()
class ExpressTask(CmdTask):
    """
    Task class for applying Express bias correction to countsfiles.

    Wraps the ``lib5c express`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the input countsfile
      * ``self.output()``: the resulting Express-normalized countsfile
    """
    bias = luigi.BoolParameter(default=True)

    def _construct_cmd_string(self):
        cmd = 'lib5c express -p %s' % self.input()[0].path
        if self.bias:
            cmd += ' -B'
        cmd += ' %s %s' % (self.input()[1].path, self.output().path)
        return cmd


@visualizable()
class KnightRuizTask(CmdTask):
    """
    Task class for applying KR bias correction to countsfiles.

    Wraps the ``lib5c kr`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the input countsfile
      * ``self.output()``: the resulting KR-normalized countsfile
    """
    bias = luigi.BoolParameter(default=True)
    imputation_size = luigi.IntParameter(default=0)

    def _construct_cmd_string(self):
        cmd = 'lib5c kr -p %s' % self.input()[0].path
        if self.bias:
            cmd += ' -B'
        if self.imputation_size is not None:
            cmd += ' -s %s' % self.imputation_size
        cmd += ' %s %s' % (self.input()[1].path, self.output().path)
        return cmd


@visualizable()
class IcedTask(CmdTask):
    """
    Task class for applying ICED bias correction to countsfiles.

    Wraps the ``lib5c iced`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the input countsfile
      * ``self.output()``: the resulting ICED-normalized countsfile
    """
    bias = luigi.BoolParameter(default=True)
    imputation_size = luigi.IntParameter(default=0)

    def _construct_cmd_string(self):
        cmd = 'lib5c iced -p %s' % self.input()[0].path
        if self.bias:
            cmd += ' -B'
        if self.imputation_size is not None:
            cmd += ' -s %s' % self.imputation_size
        cmd += ' %s %s' % (self.input()[1].path, self.output().path)
        return cmd


@visualizable()
class SplineTask(CmdTask):
    """
    Task class for applying explicit spline bias correction to countsfiles.

    Wraps the ``lib5c spline`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the input countsfile
      * ``self.output()``: the resulting spline-normalized countsfile
    """
    bias_factors = luigi.ListParameter(default=['% GC', 'length'])
    knots = luigi.ListParameter(default=[0, 20])
    model_outfile = luigi.Parameter(default=None)

    def _construct_cmd_string(self):
        cmd = 'lib5c spline -p %s' % self.input()[0].path
        if self.bias_factors is not None:
            cmd += ' -b %s' % shell_quote('(%s)' % ','.join(self.bias_factors))
        if self.knots is not None:
            cmd += ' -k %s' % \
                   shell_quote('(%s)' % ','.join([str(k) for k in self.knots]))
        cmd += ' %s %s' % (self.input()[1].path, self.output().path)
        return cmd


class DetermineBinsTask(CmdTask):
    """
    Task class for determining bin locations.

    Wraps the ``lib5c determine-bins`` command line command.

    Input/output specification:
      * ``self.input()``: the input primer .bed file
      * ``self.output()``: the resulting bin .bed file
    """
    bin_width = luigi.IntParameter(default=4000)

    def _construct_cmd_string(self):
        return 'lib5c determine-bins -w %i %s %s' % \
               (self.bin_width, self.input().path, self.output().path)


class FilteringTask(CmdTask):
    """
    Parent Task class for Tasks related to binning and smoothing.
    """
    window_width = luigi.IntParameter(default=20000)
    window_function = luigi.Parameter(default='gmean')
    threshold = luigi.FloatParameter(default=0.0)
    inverse_weights = luigi.BoolParameter(default=False)
    wipe_unsmoothable_columns = luigi.BoolParameter(default=True)

    def _construct_cmd_string(self):
        raise NotImplementedError()


@visualizable()
class BinTask(FilteringTask):
    """
    Task class for binning fragment-level countsfiles into binned countsfiles.

    Wraps the ``lib5c bin`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the bin .bed file
      * ``self.input()[1]``: the primer .bed file
      * ``self.input()[2]``: the input fragment-level countsfile
      * ``self.output()``: the resulting countsfile of binned observed values
    """
    def _construct_cmd_string(self):
        cmd = 'lib5c bin -b %s -p %s -f %s -w %i -t %s' % \
              (self.input()[0].path, self.input()[1].path, self.window_function,
               self.window_width, self.threshold)
        if self.inverse_weights:
            cmd += ' -I'
        if self.wipe_unsmoothable_columns:
            cmd += ' -W'
        cmd += ' %s %s' % (self.input()[2].path, self.output().path)
        return cmd


@visualizable()
class SmoothTask(FilteringTask):
    """
    Task class for smoothing countsfiles.

    Wraps the ``lib5c smooth`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the input observed countsfile
      * ``self.output()``: the resulting countsfile of smooth observed values
    """
    def _construct_cmd_string(self):
        cmd = 'lib5c smooth -p %s -f %s -w %i -t %s' % \
              (self.input()[0].path, self.window_function,
               self.window_width, self.threshold)
        if self.inverse_weights:
            cmd += ' -I'
        if self.wipe_unsmoothable_columns:
            cmd += ' -W'
        cmd += ' %s %s' % (self.input()[1].path, self.output().path)
        return cmd


@visualizable()
class ExpectedTask(CmdTask):
    """
    Task class for computing expected models.

    Wraps the ``lib5c expected`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the input observed countsfile
      * ``self.output()``: the resulting countsfile of expected values
    """
    monotonic = luigi.BoolParameter(default=False)
    exclude_near_diagonal = luigi.BoolParameter(default=True)
    powerlaw = luigi.BoolParameter(default=False)
    regression = luigi.BoolParameter(default=False)
    degree = luigi.IntParameter(default=1)
    lowess = luigi.BoolParameter(default=False)
    lowess_frac = luigi.FloatParameter(default=0.8)
    donut = luigi.BoolParameter(default=False)
    p = luigi.IntParameter(default=5)
    w = luigi.IntParameter(default=15)
    donut_frac = luigi.FloatParameter(default=0.2)
    min_exp = luigi.FloatParameter(default=0.1)
    log_donut = luigi.BoolParameter(default=False)
    max_with_lower_left = luigi.BoolParameter(default=False)
    log_transform = luigi.Parameter(default='auto')
    global_expected = luigi.BoolParameter(default=False)
    plot_outfile = luigi.Parameter(default=None)
    plot_outfile_kde = luigi.BoolParameter(default=False)
    plot_outfile_hexbin = luigi.BoolParameter(default=True)

    def _construct_cmd_string(self):
        cmd = 'lib5c expected -p %s -d %i -f %s -w %i -x %i -m %s -e %s ' \
            '-t %s' % (self.input()[0].path, self.degree, self.lowess_frac,
                       self.w, self.p, self.donut_frac, self.min_exp,
                       self.log_transform)
        if self.global_expected:
            cmd += ' -G'
        if self.monotonic:
            cmd += ' -M'
        if self.exclude_near_diagonal:
            cmd += ' -E'
        if self.powerlaw:
            cmd += ' -P'
        if self.regression:
            cmd += ' -R'
        if self.lowess:
            cmd += ' -L'
        if self.donut:
            cmd += ' -D'
        if self.log_donut:
            cmd += ' -O'
        if self.max_with_lower_left:
            cmd += ' -X'
        if self.plot_outfile is not None:
            if hasattr(self, 'rep'):
                cmd += ' -o %s' % self.plot_outfile.replace(r'%s', self.rep)
            else:
                cmd += ' -o %s' % self.plot_outfile
            if self.plot_outfile_kde:
                cmd += ' -K'
            if self.plot_outfile_hexbin:
                cmd += ' -B'
        cmd += ' %s %s' % (self.input()[1].path, self.output().path)
        return cmd


class VarianceTask(CmdTask):
    """
    Task class for computing variance estimates.

    Wraps the ``lib5c variance`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the input observed countsfile
      * ``self.input()[2]``: the input expected countsfile
      * ``self.output()``: the resulting countsfile of variance estimates
    """
    model = luigi.Parameter(default='lognorm')
    source = luigi.Parameter(default='deviation')
    fitter = luigi.Parameter(default='lowess')
    agg_fn = luigi.Parameter(default='lowess')
    min_obs = luigi.FloatParameter(default=2.0)
    min_disp = luigi.Parameter(default='1e-8')
    min_dist = luigi.IntParameter(default=6)
    x_unit = luigi.Parameter(default='dist')
    y_unit = luigi.Parameter(default='disp')
    logx = luigi.BoolParameter(default=False)
    logy = luigi.BoolParameter(default=False)
    regional = luigi.BoolParameter(default=False)

    def _construct_cmd_string_from_inpaths(self, obs_inpath, exp_inpath,
                                           rep=None):
        cmd = 'lib5c variance -p %s -m %s -s %s -f %s -a %s --min_obs %s ' \
              '--min_disp %s --min_dist %s --x_unit %s --y_unit %s' % \
              (self.input()[0].path, self.model, self.source, self.fitter,
               self.agg_fn, self.min_obs, self.min_disp, self.min_dist,
               self.x_unit, self.y_unit)
        if self.logx:
            cmd += ' --logx'
        if self.logy:
            cmd += ' --logy'
        if self.regional:
            cmd += ' -R'
        if rep is not None:
            cmd += ' --rep %s' % rep
        cmd += ' %s %s %s' % (obs_inpath, exp_inpath, self.output().path)
        return cmd

    def _construct_cmd_string(self):
        return self._construct_cmd_string_from_inpaths(
            self.input()[1].path, self.input()[2].path)


class CrossVarianceTask(VarianceTask):
    """
    Task class for computing variance estimates using the cross-replicate
    variance method.

    Wraps the ``lib5c variance`` command line command called with
    ``-s/--source cross_rep``.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the input expected countsfile
      * ``self.input()[2:]``: the input observed countsfiles for each replicate
      * ``self.output()``: the resulting countsfile of variance estimates

    This class defines a ``conditions`` Parameter which should be used to ensure
    that the input observed countsfiles passed in ``self.input()[2:]`` all
    belong to the same condition. This logic is not implemented here.
    """
    source = luigi.Parameter(default='cross_rep')
    conditions = luigi.Parameter(default='ES,pNPC')

    def _get_rep(self):
        if not hasattr(self, 'rep'):
            raise AttributeError('CrossVarianceTask must have rep attribute')
        return self.rep

    def _match_inputs(self):
        input_paths = [i.path for i in self.input()[2:]]
        common_prefix = os.path.commonprefix(input_paths)
        common_postfix = os.path.commonprefix(
            [p[::-1] for p in input_paths])[::-1]
        return common_prefix + '*' + common_postfix

    def _construct_cmd_string(self):
        return self._construct_cmd_string_from_inpaths(
            shell_quote(self._match_inputs()), self.input()[1].path,
            rep=self._get_rep())


@visualizable(pvalue=True)
class PvalueTask(CmdTask):
    """
    Task class for calling p-values.

    Wraps the ``lib5c pvalues`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the input observed countsfile
      * ``self.input()[2]``: the input expected countsfile
      * ``self.input()[3]``: the input variance countsfile
      * ``self.output()``: the resulting countsfile of p-values
    """
    distribution = luigi.Parameter(default='nbinom')
    log = luigi.BoolParameter(default=False)
    vst = luigi.BoolParameter(default=False)

    def _construct_cmd_string(self):
        cmd = 'lib5c pvalues -p %s %s %s %s %s %s' % \
              (self.input()[0].path, self.input()[1].path, self.input()[2].path,
               self.input()[3].path, self.distribution, self.output().path)
        if self.log:
            cmd += ' -L'
        if self.vst:
            cmd += ' -V'
        return cmd


@visualizable(tetris=True)
class ThresholdTask(CmdTask):
    """
    Task class for thresholding p-value countsfiles to call loops.

    Wraps the ``lib5c threshold`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1:]``: the input countsfiles of p-values
      * ``self.output()[0]``: the output countsfile of called loops
      * ``self.output()[1]``: the output text file summarizing the loop calls
      * ``self.output()[2]``: the output .csv file containing the complete
        analysis results
    """
    kappa_confusion_outfile = luigi.Parameter(default='kappa_confusion.txt')
    dataset_outfile = luigi.Parameter(default='dataset.tsv')
    significance_threshold = luigi.FloatParameter(default=1e-15)
    bh_fdr = luigi.BoolParameter(default=False)
    two_tail = luigi.BoolParameter(default=False)
    concordant = luigi.BoolParameter(default=False)
    distance_threshold = luigi.IntParameter(default=24000)
    size_threshold = luigi.IntParameter(3)
    background_threshold = luigi.FloatParameter(default=0.6)
    conditions = luigi.Parameter(default='ES,pNPC')

    def _construct_cmd_string(self):
        return 'lib5c threshold ' \
            '-p %s -c %s -t %s %s %s %s -s %s -d %s -b %s -o %s -k %s %s %s' \
            % (self.input()[0].path, shell_quote(self.conditions),
               self.significance_threshold, '-B' if self.bh_fdr else '',
               '-T' if self.two_tail else '', '-C' if self.concordant else '',
               self.size_threshold, self.distance_threshold,
               self.background_threshold, self.output()[1].path,
               self.output()[2].path, self.output()[0].path,
               ' '.join([x.path for x in self.input()[1:]]))


@visualizable(pvalue=True)
class QvaluesTask(CmdTask):
    """
    Task class for converting p-values to q-values.

    Wraps the ``lib5c qvalues`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the input countsfile of p-values
      * ``self.output()``: the resulting countsfile of q-values
    """
    method = luigi.Parameter(default='bh_fdr')

    def _construct_cmd_string(self):
        cmd = 'lib5c qvalues -p %s -m %s %s %s' %\
              (self.input()[0].path, self.method, self.input()[1].path,
               self.output().path)
        return cmd


@visualizable(obs_over_exp=True)
class SubtractTask(CmdTask):
    """
    Task class for subtracting one countsfile from another.

    Wraps the ``lib5c subtract`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the minuend (countsfile to subtract from)
      * ``self.input()[2]``: the subtrahend (countsfile to subtract)
      * ``self.output()``: the difference (countsfile resulting from the
        subtraction)
    """
    def _construct_cmd_string(self):
        cmd = 'lib5c subtract -p %s %s %s %s' %\
              (self.input()[0].path, self.input()[1].path, self.input()[2].path,
               self.output().path)
        return cmd


@visualizable(obs_over_exp=True)
class DivideTask(CmdTask):
    """
    Task class for dividing one countsfile by another.

    Wraps the ``lib5c divide`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the dividend (countsfile to divide)
      * ``self.input()[2]``: the divisor (countsfile to divide by)
      * ``self.output()``: the quotient (countsfile resulting from the division)
    """
    def _construct_cmd_string(self):
        cmd = 'lib5c divide -p %s %s %s %s' %\
              (self.input()[0].path, self.input()[1].path, self.input()[2].path,
               self.output().path)
        return cmd


class LogTask(CmdTask):
    """
    Task class for logging or unlogging a countsfile.

    Wraps the ``lib5c log`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the input countsfile (to be logged)
      * ``self.output()``: the resulting countsfile (after logging)
    """
    log_base = luigi.Parameter(default='e')
    pseudocount = luigi.FloatParameter(default=1)
    unlog = luigi.BoolParameter(default=False)

    def _construct_cmd_string(self):
        cmd = 'lib5c log -p %s %s -b %s -s %s %s %s' %\
              (self.input()[0].path, '-U' if self.unlog else '', self.log_base,
               self.pseudocount, self.input()[1].path, self.output().path)
        return cmd


@visualizable(obs_over_exp=True)
class InteractionScoreTask(CmdTask):
    """
    Task class for converting p-values to interaction scores.

    Wraps the ``lib5c interaction-score`` command line command.

    Input/output specification:
      * ``self.input()[0]``: the primer or bin .bed file
      * ``self.input()[1]``: the input countsfile of p-values
      * ``self.output()``: the resulting countsfile of interaction scores
    """
    def _construct_cmd_string(self):
        cmd = 'lib5c interaction-score -p %s %s %s' %\
              (self.input()[0].path, self.input()[1].path, self.output().path)
        return cmd


class DistributionTask(CmdTask):
    mode = luigi.Parameter(default='obs_over_exp')
    dist = luigi.Parameter(default='nbinom')
    log = luigi.BoolParameter(default=False)

    def _construct_cmd_string(self):
        raise NotImplementedError()


@visualizable(pvalue=True)
class LegacyPvaluesOneTask(DistributionTask):
    bias = luigi.BoolParameter(default=False)

    def _construct_cmd_string(self):
        cmd = 'lib5c pvalues -p %s -m %s -d %s' % \
              (self.input()[0].path, self.mode, self.dist)
        if self.log:
            cmd += ' -L'
        if self.bias:
            cmd += ' -b %s' % self.input()[1].path.replace('.counts', '.bias')
        cmd += ' %s %s %s' % \
               (self.input()[1].path, self.input()[2].path, self.output().path)
        return cmd


@visualizable(pvalue=True)
class LegacyPvaluesTwoTask(CmdTask):
    grouping = luigi.Parameter(default='distance')
    distance_tolerance = luigi.IntParameter(default=2)
    fractional_tolerance = luigi.FloatParameter(default=0.1)
    mode = luigi.Parameter(default='obs_over_exp')
    dist = luigi.Parameter(default='nbinom')
    log = luigi.BoolParameter(default=False)
    bias = luigi.BoolParameter(default=False)

    def _construct_cmd_string(self):
        cmd = 'lib5c pvalues2 -p %s -g %s -f %s -t %s -m %s -d %s' % \
              (self.input()[0].path, self.grouping, self.fractional_tolerance,
               self.distance_tolerance, self.mode, self.dist)
        if self.log:
            cmd += ' -L'
        if self.bias:
            cmd += ' -b %s' % self.input()[1].path.replace('.counts', '.bias')
        cmd += ' %s %s %s' % \
               (self.input()[1].path, self.input()[2].path, self.output().path)
        return cmd


class LegacyVisualizeFitTask(DistributionTask, RegionalTaskMixin):
    distance_scale = luigi.IntParameter(default=None)
    expected_value = luigi.FloatParameter(default=None)
    tolerance = luigi.FloatParameter(default=0.5)

    def _outfile_pattern(self):
        raise NotImplementedError()

    def _parameterized_outfile_pattern(self):
        # baseline outfile from pattern
        outfile = self._outfile_pattern()

        # replace parameter values
        if self.distance_scale is not None:
            outfile = outfile.replace('%d', '%i' % self.distance_scale)
        if self.expected_value is not None:
            outfile = outfile.replace('%e', '%g' % self.expected_value)
        if self.tolerance is not None:
            outfile = outfile.replace('%t', '%g' % self.tolerance)

        return outfile

    def _construct_cmd_string(self):
        cmd = 'lib5c visualize-fits -p %s -m %s -d %s' % \
              (self.input()[0].path, self.mode, self.dist)
        if self.log:
            cmd += ' -L'
        if self.distance_scale is not None:
            cmd += ' -s %i' % self.distance_scale
        if self.expected_value is not None:
            cmd += ' -e %g' % self.expected_value
        if self.tolerance is not None:
            cmd += ' -t %g' % self.tolerance
        if self.region is not None:
            cmd += ' -r %s' % self.region
        cmd += ' %s %s %s' % (self.input()[1].path,
                              self.input()[2].path,
                              self._parameterized_outfile_pattern())
        return cmd


class LegacyVisualizeVarianceTask(DistributionTask, RegionalTaskMixin):
    def _outfile_pattern(self):
        raise NotImplementedError()

    def _construct_cmd_string(self):
        cmd = 'lib5c visualize-variance -p %s -m %s -d %s' % \
              (self.input()[0].path, self.mode, self.dist)
        if self.log:
            cmd += ' -L'
        if self.region is not None:
            cmd += ' -r %s' % self.region
        cmd += ' %s %s %s' % (self.input()[1].path,
                              self.input()[2].path,
                              self._parameterized_outfile_pattern())
        return cmd
