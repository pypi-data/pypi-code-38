"""
Module implementing one particular strategy for wiring together the luigi Task
subclasses defined in ``lib5c.contrib.luigi.tasks`` into a complete pipeline.

The pipeline is organized as a tree of Tasks, which matches perfectly with a
tree of output directories. Each Task in the tree inherits from the mixin class
TreeMixin and defines a ``directory`` string parameter. This parameter
represents the output directory for that Task. Task classes can be reconstituted
from directory strings via the ``directory_to_task()`` function.

The ``directory_to_task()`` function uses the ``table`` DictParameter of the
TreeMixin, which maps user-selected short names for parameterized Tasks to Task
class names as well as detailed parameters. An example of an entry in the
``table`` is::

      "bin_amean_20_8": ["MakeBinned", {"window_function": "amean",
                                        "bin_width": 8000,
                                        "window_width": 20000}]

where the key, "bin_amean_20_8", is the user-selected short name for this
particular parameterization of the MakeBinned Task class, and the value is a
list of two elements. The first element is the Task class name as a string (in
this case, MakeBinned, which extends ``lib5c.contrib.luigi.tasks.BinTask`` and
mixes in TreeMixin). The second element is a dict containing the parameters to
construct the Task with. With this entry in the table, when a folder named
"bin_amean_20_8" occurs within the directory string, it will be interpreted as a
MakeBinned Task with the parameters specified in this table entry.

The upstream Task that a particular Task depends on (i.e., its parent in the
tree) can also be reconstituted by splitting off the last folder level in the
directory string and calling ``directory_to_task()`` on what remains. This logic
is implemented in ``TreeMixin.preceding_task()`` which allows any Task in the
tree to know what tasks precede it in the pipeline.

TreeMixin also describes ``rep`` and ``outfile_pattern`` parameters. Together
with ``directory``, these parameters specify the exact output file of running a
particular parameterized Task on one specific replicate, using the logic
implemented in ``TreeMixin.output()``.

The pipeline is orchestrated by an overall WrapperTask called PipelineTask which
stores the ``table`` and passes it through to each TreeMixin Task. It also
deduces the ``all_reps`` list (by peeking at the keys of
``RawCounts.countsfiles`` using the luigi config file) and passes it through to
each TreeMixin Task as well. It stores a list of directory strings (representing
leaf Tasks) in a ``tasks`` ListParameter. As a WrapperTask, it wraps all the
leaf Tasks in ``tasks`` and all replicates in ``all_reps`` as appropriate. The
leaf Tasks in turn use their ``directory`` strings to figure out what Tasks they
depend on. In this way the entire tree of pipeline Tasks is created from just
one PipelineTask.
"""

import os
import shutil
import ast

import luigi

import lib5c.contrib.luigi.tasks as tasks
from lib5c.util.system import splitall, shell_quote, check_outdir


def directory_to_task(directory, table, all_reps, **kwargs):
    """
    Converts a directory to a TreeMixin Task class instance, using a provided
    table.

    Parameters
    ----------
    directory : str
        The directory identifying this task.
    table : Dict[str, Tuple[str, dict[str, Any]]]
        A map from directory parts to (Task class name, param dict) tuples.
    all_reps : List[str]
        A list of all the replicates.
    kwargs : additional keyword arguments
        Will be passed to the new Task instance. The most common kwarg is 'rep'.

    Returns
    -------
    luigi.Task
        The specified Task instance.
    """
    _, current = os.path.split(directory)
    class_name, params = table[current]
    params = dict(params.items())
    params.update(table=table, directory=directory, all_reps=all_reps)
    params.update(**kwargs)
    instance = globals()[class_name](**params)
    return instance


class TreeMixin(object):
    """
    Core mixin class for pipeline Tasks. See the module docstring for more
    details.

    If mixed with a ``lib5c.contrib.luigi.tasks.CmdTask`` subclass, the only
    luigi function that the derived class needs to implement is ``requires()``.
    """
    table = luigi.DictParameter()
    directory = luigi.Parameter()
    outfile_pattern = luigi.Parameter()
    rep = luigi.Parameter(default=None)
    all_reps = luigi.ListParameter()

    def preceding_task(self, rep=None):
        """
        Returns the Task instance that precedes this Task.

        Parameters
        ----------
        rep : str, optional
            The replicate name to parameterize the parent Task with. Pass None
            if the Task is not a per-rep Task.

        Returns
        -------
        luigi.Task
            The Task instance that precedes this Task.
        """
        return directory_to_task(os.path.split(self.directory)[0],
                                 self.table, self.all_reps, rep=rep)

    def locus_info_task(self):
        """
        Returns the Task instance corresponding to the primerfile or binfile
        needed by this Task.

        Returns
        -------
        luigi.Task
            The Task instance corresponding to the primerfile or binfile needed
            by this Task.
        """
        # walk directory to see if you hit something that maps to MakeBinned
        # if you do, return DetermineBins with the indicated bin width
        # otherwise, return PrimerFile
        all_steps = splitall(self.directory)[::-1]
        for step in all_steps:
            if self.table[step][0] == 'MakeBinned':
                bin_width = self.table[step][1].get('bin_width')
                if bin_width is not None:
                    return DetermineBins(bin_width=bin_width)
                else:
                    return DetermineBins()
        return PrimerFile()

    def output(self):
        """
        Returns the luigi Target corresponding to the output file that is the
        direct result of running this Task.

        Returns
        -------
        luigi.Target
            The Target corresponding to the output file that is the direct
            result of running this Task.
        """
        full_outfile = os.path.join(self.directory, self.outfile_pattern)
        if self.rep is None:
            return luigi.LocalTarget(full_outfile)
        else:
            return luigi.LocalTarget(full_outfile % self.rep)


class PerRepSimpleTreeMixin(TreeMixin):
    """
    Mixin class that adds the most common implementation of ``requires()`` to
    TreeMixin.

    Most pipeline Tasks depend on two inputs: a primer or binfile, and the
    immediately preceding countsfile for the rep of the child Task.

    Pipeline Tasks that depend on more than one countsfile (e.g., p-value
    calling), or all replicates (e.g., thresholding) cannot use this mixin,
    and instead must inherit from TreeMixin and define their own implementation
    of ``requires()``.
    """
    def requires(self):
        return self.locus_info_task(), self.preceding_task(rep=self.rep)


class JointTask(TreeMixin, luigi.WrapperTask):
    """
    Mixin class for pipeline Tasks that operate on input from all replicates.

    Tasks inheriting from JointTask become WrapperTasks, one of which can be
    created for each replicate, but each of which will depend on the same inner
    Task which does the actual work. In terms of the overall pipeline flow, this
    allows a piece of ``directory`` to map to a JointTask, which can be
    instantiated once for each replicate via the ``rep`` kwarg of the TreeMixin.
    All the JointTask instances will depend on a single inner Task inheriting
    from JointInnerMixin that actually does the work.

    Tasks inheriting from JointTask must implement ``get_inner_task_class()``,
    which should return a Task class which inherits from JointInnerMixin and
    actually does the work.

    Since ``get_inner_task_class()`` just returns a Task class which must still
    be instantiated with the proper parameters, JointTask provides an
    overrideable hook, ``get_inner_task_params()`` to allow Task classes which
    inherit from JointTask to manually pass their parameters through to the
    inner Task. See ``MakeQnorm.get_inner_task_params()`` for an example.

    The related helper function ``get_inner_task_param_dict()`` helps to
    simplify this process by automatically passing through key TreeMixin
    parameters like ``table``, ``directory``, ``all_reps``, and the
    ``@visualizable`` visualization hook parameters.
    """
    rep = luigi.Parameter()
    outfile_pattern = luigi.Parameter(default=None)

    def get_inner_task_class(self):
        raise NotImplementedError()

    def get_inner_task_params(self):
        """
        Hook to allow subclasses to supply extra parameters to their inner
        Tasks. Subclasses should override this function.

        Returns
        -------
        dict
            Extra parameters to be supplied to the inner task upon construction.
        """
        return {}

    def get_inner_task_param_dict(self):
        """
        Constructs the complete dict of params for inner task instantiation.

        Provides some important core defaults in the context of the tree
        pipeline, and injects whatever parameters are returned by
        ``get_inner_task_params()``.

        This is a helper function - subclasses should not override this function
        and should override ``get_inner_task_params()`` instead.

        Returns
        -------
        dict
            The complete dict of params.
        """
        inner_task_params = self.get_inner_task_params()
        inner_task_params.update(table=self.table, directory=self.directory,
                                 all_reps=self.all_reps)
        if hasattr(self, 'outfile_pattern'):
            inner_task_params.update(outfile_pattern=self.outfile_pattern)
        if hasattr(self, 'heatmap'):
            inner_task_params.update(heatmap=self.heatmap)
        if hasattr(self, 'heatmap_outdir'):
            inner_task_params.update(heatmap_outdir=self.heatmap_outdir)
        return inner_task_params

    def get_rep_index(self):
        """
        Returns the index of the replicate this Task wraps the output for among
        all the replicates (in the order of ``self.all_reps``).

        Returns
        -------
        int
            The index of the replicate this Task wraps the output for among all
            the replicates (in the order of ``self.all_reps``).
        """
        return self.all_reps.index(self.rep)

    def requires(self):
        """
        Universal implementation of ``requires()`` for JointTasks.

        Simply put, the JointTask depends on its inner Task class, instantiated
        using the parameters obtained from ``get_inner_task_params()`` via
        ``get_inner_task_param_dict()``.

        Returns
        -------
        luigi.Task
            The Task instance of the inner Task that this WrapperTask depends
            on.
        """
        return self.get_inner_task_class()(**self.get_inner_task_param_dict())

    def output(self):
        """
        Universal implementation of ``output()`` for JointTasks.

        This implementation simply instantiates the inner Task and asks it for
        its outputs, returning the one that corresponds to the replicate of this
        JointTask. The assumption here is that the inner Task class's
        ``output()`` will be a list whose elements correspond to the replicates
        in ``all_reps``.

        Returns
        -------
        luigi.Target
            The Target of this JointTask.
        """
        return self.get_inner_task_class()(**self.get_inner_task_param_dict())\
            .output()[self.get_rep_index()]


class JointInnerMixin(object):
    """
    Mixin class for inner Tasks wrapped by JointTask.

    The inner Task of a JointTask depends on the preceding Task's output for all
    replicates.

    This mixin provides a helper function ``_match_input()`` which subclasses
    can use to get a glob-based pattern that matches all the input files for the
    Task which precedes this Task. CmdTasks inheriting from this mixin only need
    to use this approach if they must describe all their input files using a
    single string (see JointExpressInnerTask for an example). CmdTasks that can
    simply list the exact input files they depend on can use something like::

        [i.path for i in self.input()]

    See QnormInnerTask for an example of this second approach.

    A basic implementation of ``requires()`` is provided here and should work in
    most cases, but Task classes inheriting from JointInnerMixin must still
    define their own implementation of ``output()``.
    """
    def _match_inputs(self):
        """
        Returns a glob-based string which should match the output countsfiles of
        the preceding Task for all replicates.

        Returns
        -------
        str
            Pattern that should match the output countsfiles of the preceding
            Task for all replicates.
        """
        preceding_task = self.preceding_task(rep=self.all_reps[0])
        return os.path.join(preceding_task.directory,
                            preceding_task.outfile_pattern.replace('%s', '*'))

    def requires(self):
        """
        Basic implementation of ``requires()`` for inner Tasks of a JointTask.

        This basic implementation assumes that the inner Task depends on the
        locus file and the preceding Task for each replicate in ``all_reps``.

        Subclasses may override this if they depend on more than just these
        inputs.

        Returns
        -------
        list of luigi.Task
            The Tasks that this inner Task depends on.
        """
        return [self.locus_info_task()] + \
            [self.preceding_task(rep=rep) for rep in self.all_reps]


class JointInnerParallelMixin(JointInnerMixin):
    """
    Mixin class providing a simple implementation of ``output()`` for Task
    classes inheriting from JointInnerMixin.
    """
    def output(self):
        """
        Simple implementation of ``output()`` for Task classes inheriting from
        JointInnerMixin.

        This implemntation assumes that the output files are parallel to the
        input files (i.e., there is one for each replicate and it can be
        obtained by interpolating ``rep`` into the ``outfile_pattern``).

        Returns
        -------
        list of luigi.Target
            The Targets of this inner Task.
        """
        full_outfile = os.path.join(self.directory, self.outfile_pattern)
        return [luigi.LocalTarget(full_outfile % rep) for rep in self.all_reps]


class RawCounts(TreeMixin, luigi.ExternalTask):
    """
    Pipeline Task for finding the raw input countsfiles on the disk.

    This step is not resolved through the ``table``, but instead uses its own
    DictParameter ``countsfiles`` which should map replicate names to the paths
    of the raw input countsfiles on the disk.
    """
    rep = luigi.Parameter()
    countsfiles = luigi.DictParameter()
    outfile_pattern = luigi.Parameter(default=None)

    def output(self):
        """
        Looks up the location of the countsfile for this replicate using the
        ``countsfiles`` DictParameter and returns a LocalTarget pointing to it.

        Returns
        -------
        luigi.Target
            The Target corresponding to the raw input countsfile represented by
            this Task.
        """
        return luigi.LocalTarget(self.countsfiles[self.rep])


@tasks.visualizable()
class MakeRaw(PerRepSimpleTreeMixin, luigi.Task):
    """
    Pipeline Task for performing the "raw" step of the pipeline.

    This step doesn't actually do anything, so it just copies over the input
    countsfile (which is actually represented by a RawCounts Task) into the
    output directory tree. By having a separate step for this we guarantee that
    a) a raw countsfile can be found with a predictable name (in agreement with
    the replicate names which are set by the keys of ``RawCounts.countsfiles``)
    and in a predictable spot in the output directory structure, and b) the raw
    countsfile can be visualized using the same visualization hooks as any other
    step.
    """
    def run(self):
        """
        Simply copies the raw countsfile to its expected spot in the output
        directory structure.
        """
        check_outdir(self.output().path)
        shutil.copy(self.input()[1].path, self.output().path)


class PrimerFile(luigi.ExternalTask):
    """
    Pipeline Task for finding the input primerfile on the disk.
    """
    primerfile = luigi.Parameter()

    def output(self):
        """
        Implementation of ``output()``.

        Returns
        -------
        luigi.Target
            A LocalTarget pointing to this Task's ``primerfile`` parameter,
            which should be the location of the input primerfile on the disk.
        """
        return luigi.LocalTarget(self.primerfile)


class DetermineBins(tasks.DetermineBinsTask):
    """
    Pipeline Task for DetermineBinsTask (the step which decides how to bin the
    5C regions).

    This Task is pre-wired to depend on the PrimeFile pipeline Task, and to
    write its output to an output folder called `bedfiles/`.
    """
    def requires(self):
        """
        Implementation of ``requires()``, pre-wired to depend on the PrimerFile
        pipeline Task.

        Returns
        -------
        luigi.Task
            The Task that this Task depends on.
        """
        return PrimerFile()

    def output(self):
        """
        Implementation of ``output()``, pre-wired to write the output to the
        `bedfiles/` folder.

        Returns
        -------
        luigi.Target
            The Target of this Task.
        """
        return luigi.LocalTarget('bedfiles/%ikb_bins.bed' %
                                 (self.bin_width/1000))


class MakeRemoved(PerRepSimpleTreeMixin, tasks.OutliersTask):
    """
    Pipeline Task class for the high outlier removal step. All functionality is
    handled by PerRepSimpleTreeMixin.
    """
    pass


@tasks.visualizable()
class MakeQnorm(JointTask):
    """
    Outer wrapper pipeline JointTask for the qnorm step.
    """
    regional = luigi.BoolParameter(default=False)
    averaging = luigi.BoolParameter(default=False)
    condition_on = luigi.Parameter(default=None)
    reference = luigi.Parameter(default=None)

    def get_inner_task_class(self):
        """
        Points to QnormInnerTask, the inner Task for the qnorm step.

        Returns
        -------
        luigi.Task
            The inner Task class for this JointTask.
        """
        return QnormInnerTask

    def get_inner_task_params(self):
        """
        Passes through all the parameters for the qnorm step.

        Returns
        -------
        dict
            The parameters for the qnorm step.
        """
        return {'regional': self.regional,
                'averaging': self.averaging,
                'condition_on': self.condition_on,
                'reference': self.reference}


class QnormInnerTask(JointInnerParallelMixin, TreeMixin, tasks.QnormTask):
    """
    Inner Task class for the MakeQnorm JointTask.
    """
    def _construct_cmd_string(self):
        """
        Overrides ``QnormTask._construct_cmd_string()`` in order to prepend
        ``directory`` to the output countsfile pattern.

        This is necessary because ``QnormTask._construct_cmd_string()`` uses
        ``outfile_pattern`` instead of ``output()`` to construct the part of the
        command string that corresponds to the outfile pattern. This is a
        problem because pipeline Tasks expect ``output_pattern`` to be relative
        to the ``directory``, but since QnormTask doesn't know about
        ``directory`` it is implicitly assuming that ``output_pattern`` is
        relative to the root of the output folder structure. If
        ``QnormTask._construct_cmd_string()`` reconstructed the part of the
        command string that corresponds to the outfile pattern by constructing a
        pattern based on ``output()`` instead of using ``outfile_pattern``, this
        override would not be necessary.

        Returns
        -------
        str
            The command line string for this CmdTask.
        """
        cmd = 'lib5c qnorm -p %s' % self.input()[0].path
        if self.regional:
            cmd += ' -R'
        if self.averaging:
            cmd += ' -A'
        if self.condition_on is not None:
            cmd += ' -c %s' % shell_quote(self.condition_on)
        if self.reference is not None:
            cmd += ' -r %s' % shell_quote(self.reference)
        cmd += ' %s %s' % (os.path.join(self.directory, self.outfile_pattern),
                           ' '.join(i.path for i in self.input()[1:]))
        return cmd


class MakeExpress(PerRepSimpleTreeMixin, tasks.ExpressTask):
    """
    Pipeline Task class for the express step. All functionality is handled by
    PerRepSimpleTreeMixin.
    """
    pass


@tasks.visualizable()
class MakeJointExpress(JointTask):
    """
    Outer wrapper pipeline JointTask for the joint express step.
    """
    def get_inner_task_class(self):
        """
        Points to JointExpressInnerTask, the inner Task for the joint express
        step.

        Returns
        -------
        luigi.Task
            The inner Task class for this JointTask.
        """
        return JointExpressInnerTask


class JointExpressInnerTask(JointInnerParallelMixin, TreeMixin,
                            tasks.ExpressTask):
    """
    Inner Task class for the MakeJointExpress JointTask.
    """
    def _construct_cmd_string(self):
        """
        Overrides ``ExpressTask._construct_cmd_string()`` to add the
        ``-J/--joint`` flag and to replace the part of the string corresponding
        to the output file with ``outfile_pattern`` appended to ``directory``.

        Returns
        -------
        str
            The command line string for this CmdTask.
        """
        cmd = 'lib5c express -J -p %s' % self.input()[0].path
        if self.bias:
            cmd += ' -B'
        cmd += ' %s %s' % (shell_quote(self._match_inputs()),
                           os.path.join(self.directory, self.outfile_pattern))
        return cmd


class MakeKR(PerRepSimpleTreeMixin, tasks.KnightRuizTask):
    """
    Pipeline Task class for the Knight-Ruiz balancing step. All functionality is
    handled by PerRepSimpleTreeMixin.
    """
    pass


class MakeIced(PerRepSimpleTreeMixin, tasks.IcedTask):
    """
    Pipeline Task class for the ICED balancing step. All functionality is
    handled by PerRepSimpleTreeMixin.
    """
    pass


class MakeSpline(PerRepSimpleTreeMixin, tasks.SplineTask):
    """
    Pipeline Task class for the explicit spline normalization step. All
    functionality is handled by PerRepSimpleTreeMixin.
    """
    pass


class MakeSmoothed(PerRepSimpleTreeMixin, tasks.SmoothTask):
    """
    Pipeline Task class for the smoothing step. All functionality is handled by
    PerRepSimpleTreeMixin.
    """
    pass


class MakeBinned(TreeMixin, tasks.BinTask):
    """
    Pipeline Task class for the binning step.

    Unlike most countsfile-to-countsfile steps, the binning step needs to use
    two different locus Tasks as input: the primerfile and the binfile.
    Therefore, this class must provide a custom implementation of ``requires()``
    to specify this.
    """
    bin_width = luigi.IntParameter(default=4000)

    def requires(self):
        """
        Depends on both the binfile (represented by a DetermineBins instance)
        and the primerfile (represented by the PrimerFile instance) in addition
        to the preceding Task.

        Returns
        -------
        tuple of luigi.Task
            The Tasks this Task depends on.
        """
        return (DetermineBins(bin_width=self.bin_width), PrimerFile(),
                self.preceding_task(rep=self.rep))


class MakeExpected(PerRepSimpleTreeMixin, tasks.ExpectedTask):
    """
    Pipeline Task class for the expected modeling step. All functionality is
    handled by PerRepSimpleTreeMixin.
    """
    pass


class MakeVariance(TreeMixin, tasks.VarianceTask):
    """
    Pipeline Task for the variance modeling step.
    """
    def requires(self):
        """
        Depends on both the preceding Task (assumed to be the expected counts)
        and the Task that precedes that Task (assumed to be the observed
        counts).

        Returns
        -------
        tuple of luigi.Task
            The Tasks this Task depends on.
        """
        exp_task = self.preceding_task(rep=self.rep)
        obs_task = exp_task.preceding_task(rep=self.rep)
        return self.locus_info_task(), obs_task, exp_task


class MakeCrossVariance(TreeMixin, tasks.CrossVarianceTask):
    """
    Pipeline Task for the cross-replicate variance modeling step.

    Even though this Task depends on multiple replicates, it is not implemented
    as a JointTask.
    """
    def requires(self):
        """
        Depends on the preceding Task for the same replicate (assumed to be the
        expected counts) and the Task that precedes that Task (assumed to be the
        observed counts) for all replicates in this Task's condition.

        This Task's condition is inferred to be the first condition in the
        comma-separated string parameter ``conditions`` that is a substring of
        ``rep``. Other replicates match this condition if this condition is also
        a substring of their replicate names.

        Returns
        -------
        list of luigi.Task
            The Tasks this Task depends on. The first Task is the locus info
            Task, the second is the expected Task for this replicate, and the
            remaining Tasks in the list are observed Tasks for all replicates in
            the same condition as this replicate.
        """
        cond = next(c for c in self.conditions.split(',') if c in self.rep)
        exp_task = self.preceding_task(rep=self.rep)
        obs_tasks = [exp_task.preceding_task(rep=r) for r in self.all_reps
                     if cond in r]
        return [self.locus_info_task(), exp_task] + obs_tasks


class MakePvalues(TreeMixin, tasks.PvalueTask):
    """
    Pipeline Task for the p-value calling step.
    """
    def requires(self):
        """
        Depends on three Tasks: the preceding Task (assumed to be the variance
        counts), the Task that precedes that Task (assumed to be the expected
        counts) and the Task that precedes that Task (assumed to be the observed
        counts).

        Returns
        -------
        tuple of luigi.Task
            The Tasks this Task depends on.
        """
        var_task = self.preceding_task(rep=self.rep)
        exp_task = var_task.preceding_task(rep=self.rep)
        obs_task = exp_task.preceding_task(rep=self.rep)
        return self.locus_info_task(), obs_task, exp_task, var_task


class MakeThreshold(JointInnerMixin, TreeMixin, tasks.ThresholdTask):
    """
    Pipeline Task for the loop call thresholding step.

    This Task is implemented as if it were the inner Task of a JointTask, but
    since there is only one ThresholdTask for all replicates, it does not need a
    corresponding WrapperTask to wrap itself across replicates.

    It gets its implementation of ``requires()`` from JointInnerMixin, which
    correctly depends on the output of the preceding Task (assumed to be the
    p-values) across ``all_reps``.
    """
    def output(self):
        """
        Specifies the output file locations for the thresholding step.

        These locations are controlled by the ``outfile_pattern`` (countsfile of
        final cluster assignments), ``dataset_outfile`` (table of complete
        results), and ``kappa_confusion_outfile`` (text file of summary
        information and concordance metrics).

        Returns
        -------
        tuple of luigi.Target
            The Targets resulting from this Task.
        """
        return (
            luigi.LocalTarget(
                os.path.join(self.directory, self.outfile_pattern)),
            luigi.LocalTarget(
                os.path.join(self.directory, self.dataset_outfile)),
            luigi.LocalTarget(
                os.path.join(self.directory, self.kappa_confusion_outfile))
        )


class MakeQvalues(PerRepSimpleTreeMixin, tasks.QvaluesTask):
    """
    Pipeline Task class for the multiple testing correction step, which converts
    p-values to q-values. All functionality is handled by PerRepSimpleTreeMixin.

    Note that the thresholding step performs its own multiple testing correction
    when parameterized with ``bh_fdr=True``, so this step is never required.
    """
    pass


class MakeObsMinusExp(TreeMixin, tasks.SubtractTask):
    """
    Pipeline Task class for the obs-exp step (analogous to the obs/exp step but
    for data that have already been log-transformed).
    """
    def requires(self):
        """
        Depends on both the preceding Task (assumed to be the expected counts)
        and the Task that precedes that Task (assumed to be the observed
        counts).

        Returns
        -------
        tuple of luigi.Task
            The Tasks this Task depends on.
        """
        exp_task = self.preceding_task(rep=self.rep)
        obs_task = exp_task.preceding_task(rep=self.rep)
        return self.locus_info_task(), obs_task, exp_task


class MakeObsOverExp(TreeMixin, tasks.DivideTask):
    """
    Pipeline Task class for the obs/exp step.
    """
    def requires(self):
        """
        Depends on both the preceding Task (assumed to be the expected counts)
        and the Task that precedes that Task (assumed to be the observed
        counts).

        Returns
        -------
        tuple of luigi.Task
            The Tasks this Task depends on.
        """
        exp_task = self.preceding_task(rep=self.rep)
        obs_task = exp_task.preceding_task(rep=self.rep)
        return self.locus_info_task(), obs_task, exp_task


class MakeLogged(PerRepSimpleTreeMixin, tasks.LogTask):
    """
    Pipeline Task class for LogTask. All functionality is handled by
    PerRepSimpleTreeMixin.
    """
    pass


class MakeInteractionScores(PerRepSimpleTreeMixin, tasks.InteractionScoreTask):
    """
    Pipeline Task class for InteractionScoreTask. All functionality is handled
    by PerRepSimpleTreeMixin.
    """
    pass


class MakeLegacyPvaluesOne(TreeMixin, tasks.LegacyPvaluesOneTask):
    def requires(self):
        exp_task = self.preceding_task(rep=self.rep)
        obs_task = exp_task.preceding_task(rep=self.rep)
        return self.locus_info_task(), obs_task, exp_task


class PipelineTask(luigi.WrapperTask):
    """
    Overall wrapper Task that orchestrates the entire pipeline.

    Running this Task runs every leaf Task in the ``tasks`` ListParameter as
    well as all parent Tasks needed to get from the root (raw input countsfiles)
    to those leaves.

    Tasks should be specified in the ``tasks`` ListParameter in the form of
    directory strings to the leaf Tasks (final step in a chain of Tasks).

    Individual folders in the directory strings in ``tasks`` will be converted
    to properly parameterized Task instances via the ``table`` DictParameter,
    which should map folder names to lists of two items: the appropriate
    pipeline Task class name as a string, and a dict of parameters to
    instantiate that Task class with. See the module docstring for an example.

    The leaf Tasks will automatically be parallelized across ``all_reps`` unless
    they are MakeThreshold (the Task class for which ``rep`` is always None).
    """
    table = luigi.DictParameter()
    tasks = luigi.ListParameter()

    def requires(self):
        """
        Deduces ``all_reps`` and wraps all the leaf Tasks in ``tasks`` over all
        replicates if appropriate, passing though ``table`` and ``all_reps``.
        """
        # deduce all_reps
        all_reps = ast.literal_eval(
            luigi.configuration.LuigiConfigParser.instance().get(
                'RawCounts', 'countsfiles')).keys()

        for task in self.tasks:
            # check to see what kind of task this is
            class_name, _ = self.table[os.path.split(task)[1]]
            if class_name == 'MakeThreshold':  # don't parallelize across reps
                yield directory_to_task(task, self.table, all_reps)
            else:
                for rep in all_reps:
                    yield directory_to_task(
                        task, self.table, all_reps, rep=rep)
