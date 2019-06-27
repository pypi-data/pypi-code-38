from bamboo_lib.models import BasePipeline
from bamboo_lib.models import PipelineStep, ComplexPipelineExecutor  # ,Connector


class DummyStep(PipelineStep):
    def run_step(self, prev, params):
        return prev


class DummyPipeline(BasePipeline):
    @staticmethod
    def pipeline_id():
        return 'dummy'

    @staticmethod
    def name():
        return 'Dummy Pipeline'

    @staticmethod
    def description():
        return 'For testing only'

    @staticmethod
    def website():
        return 'https://www.census.gov/programs-surveys/acs/data/pums.html'

    @staticmethod
    def parameter_list():
        return []

    @staticmethod
    def run(params_dict, **kwargs):
        pp = ComplexPipelineExecutor({})
        pp.next(DummyStep())
        return pp.run_pipeline()
