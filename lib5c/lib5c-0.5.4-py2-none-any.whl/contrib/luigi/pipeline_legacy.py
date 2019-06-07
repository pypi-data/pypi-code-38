"""
This module provides a baseline implementation of a 5C pipeline that assumes
that many of the steps of the pipeline are parametrized by replicate and that
these steps can be chained together.
"""

import os
import ast
import uuid

import luigi

import lib5c.contrib.luigi.tasks as tasks
from lib5c.util.system import shell_quote


def parallelize_reps_chained(task_class, pipeline_config, reps, **kwargs):
    return type(
        '%sWrapper_%s' % (task_class.__name__, str(uuid.uuid4())[:8]),
        (luigi.WrapperTask,),
        {'requires': lambda self: [task_class(rep=rep,
                                              pipeline_config=pipeline_config,
                                              **kwargs)
                                   for rep in reps]})


class ChainableMixin(object):
    pipeline_config = luigi.DictParameter()

    @classmethod
    def get_class_name(cls):
        return cls.__name__

    def locus_info_task(self):
        if self.pipeline_config[self.get_class_name()]['level'] == 'bin':
            return DetermineBins()
        elif self.pipeline_config[self.get_class_name()]['level'] == 'fragment':
            return PrimerFile()

    def preceding_task_class(self):
        return globals()[
            self.pipeline_config[self.get_class_name()]['preceding_step']]

    def preceding_task(self, **kwargs):
        return self.preceding_task_class()(pipeline_config=self.pipeline_config,
                                           **kwargs)


class PerRepCountsTaskMixin(object):
    rep = luigi.Parameter()
    outfile_pattern = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.outfile_pattern % self.rep)


class PerRepSimpleChainableMixin(PerRepCountsTaskMixin, ChainableMixin):
    def requires(self):
        return self.locus_info_task(), self.preceding_task(rep=self.rep)


class RawCounts(ChainableMixin, luigi.ExternalTask):
    rep = luigi.Parameter()
    countsfiles = luigi.DictParameter()

    def output(self):
        return luigi.LocalTarget(self.countsfiles[self.rep])


class PrimerFile(luigi.ExternalTask):
    primerfile = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.primerfile)


class MakeRemoved(PerRepSimpleChainableMixin, tasks.OutliersTask):
    pass


class DetermineBins(tasks.DetermineBinsTask):
    def requires(self):
        return PrimerFile()

    def output(self):
        return luigi.LocalTarget('bedfiles/4kb_bins.bed')


class MakeBinned(PerRepCountsTaskMixin, ChainableMixin, tasks.BinTask):
    def requires(self):
        return DetermineBins(), PrimerFile(), self.preceding_task(rep=self.rep)


class MakeSmoothed(PerRepSimpleChainableMixin, tasks.SmoothTask):
    pass


class JointTask(ChainableMixin, luigi.WrapperTask):
    rep = luigi.Parameter()

    def get_inner_task_class(self):
        raise NotImplementedError()

    def get_rep_index(self):
        return self.pipeline_config['reps'].index(self.rep)

    def requires(self):
        return self.get_inner_task_class()(pipeline_config=self.pipeline_config)

    def output(self):
        return self.get_inner_task_class()(
            pipeline_config=self.pipeline_config).output()[
                self.get_rep_index()]


class MakeQnorm(JointTask):
    def get_inner_task_class(self):
        return QnormInnerTask


@tasks.visualizable()
class QnormInnerTask(ChainableMixin, tasks.QnormTask):
    def requires(self):
        return [self.locus_info_task()] + \
               [self.preceding_task(rep=rep)
                for rep in self.pipeline_config['reps']]

    def output(self):
        return [luigi.LocalTarget(self.outfile_pattern % rep)
                for rep in self.pipeline_config['reps']]


class MakeExpress(PerRepSimpleChainableMixin, tasks.ExpressTask):
    pass


class MakeJointExpress(JointTask):
    def get_inner_task_class(self):
        return JointExpressInnerTask


@tasks.visualizable()
class JointExpressInnerTask(ChainableMixin, tasks.ExpressTask):
    outfile_pattern = luigi.Parameter(default='express/%s_express.counts')

    def _match_inputs(self):
        input_paths = [i.path for i in self.input()[1:]]
        common_prefix = os.path.commonprefix(input_paths)
        common_postfix = os.path.commonprefix(
            [p[::-1] for p in input_paths])[::-1]
        return common_prefix + '*' + common_postfix

    def requires(self):
        return [self.locus_info_task()] + \
               [self.preceding_task(rep=rep)
                for rep in self.pipeline_config['reps']]

    def output(self):
        return [luigi.LocalTarget(self.outfile_pattern % rep)
                for rep in self.pipeline_config['reps']]

    def _construct_cmd_string(self):
        cmd = 'lib5c express -J -p %s' % self.input()[0].path
        if self.bias:
            cmd += ' -B'
        cmd += ' %s %s' % (shell_quote(self._match_inputs()),
                           self.outfile_pattern)
        return cmd


class MakeKR(PerRepSimpleChainableMixin, tasks.KnightRuizTask):
    pass


class MakeIced(PerRepSimpleChainableMixin, tasks.IcedTask):
    pass


class MakeSpline(PerRepSimpleChainableMixin, tasks.SplineTask):
    pass


class MakeExpected(PerRepSimpleChainableMixin, tasks.ExpectedTask):
    pass


class MakeLegacyPvaluesOne(PerRepCountsTaskMixin, ChainableMixin,
                           tasks.LegacyPvaluesOneTask):
    def requires(self):
        return self.locus_info_task(), self.preceding_task(rep=self.rep), \
            MakeExpected(rep=self.rep, pipeline_config=self.pipeline_config)


class MakeLegacyPvaluesTwo(PerRepCountsTaskMixin, ChainableMixin,
                           tasks.LegacyPvaluesTwoTask):
    def requires(self):
        return self.locus_info_task(), self.preceding_task(rep=self.rep), \
            MakeExpected(rep=self.rep, pipeline_config=self.pipeline_config)


class PipelineTask(luigi.WrapperTask):
    step_order = luigi.ListParameter(
        default=['MakeRemoved', 'MakeBinned', 'MakeExpress', 'MakeExpected',
                 'MakePvalues'])
    initial_level = luigi.Parameter(default='fragment')

    def requires(self):
        # deduce all_reps
        all_reps = ast.literal_eval(
            luigi.configuration.LuigiConfigParser.instance().get(
                'RawCounts', 'countsfiles')).keys()

        # construct pipeline_config
        pipeline_config = {'reps': all_reps}
        current_level = self.initial_level
        preceding_class_str = 'RawCounts'
        for class_str in self.step_order:
            if class_str == 'MakeBinned':
                current_level = 'bin'
            if class_str == 'MakeJointExpress':
                pipeline_config['JointExpressInnerTask'] = {
                    'level'         : current_level,
                    'preceding_step': preceding_class_str}
            if class_str == 'MakeQnorm':
                pipeline_config['QnormInnerTask'] = {
                    'level'         : current_level,
                    'preceding_step': preceding_class_str}
            pipeline_config[class_str] = {
                'level'         : current_level,
                'preceding_step': preceding_class_str}
            if class_str != 'MakeExpected':
                preceding_class_str = class_str

        # parallelize the last step in the chain across all reps
        return parallelize_reps_chained(
            globals()[self.step_order[-1]], pipeline_config, all_reps)()
