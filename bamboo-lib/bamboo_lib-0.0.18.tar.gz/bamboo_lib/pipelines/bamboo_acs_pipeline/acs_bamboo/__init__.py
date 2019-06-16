from bamboo_lib.models import Parameter, BasePipeline
import acs_bamboo.standard_acs as standard_acs

from acs_bamboo.standard_acs import ZIP, PLACE, TRACT, COUNTY, STATE, NATION, MSA
from os.path import dirname, abspath, join
from os import listdir
SUM_LEVELS = [ZIP, PLACE, TRACT, COUNTY, STATE, NATION, MSA]


def get_parent_dir():
    parent_dir = dirname(dirname(abspath(__file__)))
    return join(parent_dir, "config")


def get_configs():
    parent_dir = get_parent_dir()
    configs = [join(parent_dir, f) for f in listdir(parent_dir)]
    return configs


class AcsPipeline(BasePipeline):

    @staticmethod
    def pipeline_id():
        return 'bamboo-acs-pipeline'

    @staticmethod
    def name():
        return 'ACS Pipeline'

    @staticmethod
    def description():
        return 'Processes data from ACS Summary Files'

    @staticmethod
    def website():
        return 'https://www.census.gov/programs-surveys/acs/data.html'

    @staticmethod
    def parameter_list():
        source_list = get_configs()
        return [
            Parameter(label="Source", name="pipeline_config_path", dtype=str, options=source_list),
            Parameter(name="year", dtype=int, allow_multiple=True,
                      options=range(2009, 2017)),
            Parameter(name="sumlevels", options=SUM_LEVELS, dtype=str),
            Parameter(name="estimate", dtype=int, options=[1, 5]),
            Parameter(label="Save results in database", name="write-to-db", dtype=bool, options=[True, False])
        ]

    @staticmethod
    def run(params_dict, **kwargs):
        print(params_dict)
        return standard_acs.run(params_dict)

    @staticmethod
    def get_sources():
        print(get_configs())
