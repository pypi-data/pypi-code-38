from bamboo_lib.models import Parameter, BasePipeline
from bamboo_lib.pipelines.pums.pums_runner import run
from bamboo_lib.connectors.models import Connector


class PumsPipeline(BasePipeline):
    @staticmethod
    def pipeline_id():
        return 'pums'

    @staticmethod
    def name():
        return 'PUMS Pipeline'

    @staticmethod
    def description():
        return 'Processes data from PUMS'

    @staticmethod
    def website():
        return 'https://www.census.gov/programs-surveys/acs/data/pums.html'

    @staticmethod
    def parameter_list():
        return [
            Parameter(name="year", dtype=int, allow_multiple=False, options=[2013, 2014, 2015, 2016]),
            Parameter(name="estimate", dtype=int, options=[1, 5]),
            Parameter(name="regional-mode", dtype=bool, options=["us", "pr"]),
            Parameter(label="Save results in database", name="write-to-db", dtype=bool, options=[True, False]),
            Parameter(label="Only generate schema", name="only-gen-schema", dtype=bool),
            Parameter(label="Output database connector", name="output-db", dtype=str, source=Connector)
        ]

    @staticmethod
    def run(params_dict, **kwargs):
        return run(params_dict)
