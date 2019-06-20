import os

from bamboo_lib.models import PipelineStep, LinearPipelineExecutor
from bamboo_lib.steps import LoadStep
import pandas as pd
from bamboo_lib.connectors.models import Connector

from acs_core.fetch import Fetcher
from acs_core.pipeline import CubeGenerator

import yaml

# These are the geo hierarchy identifiers used to make api call.
# copied from fetch?
ZIP = "zip code tabulation area"
PLACE = 'place'
TRACT = 'tract'
COUNTY = 'county'
STATE = 'state'
NATION = 'us'
MSA = 'metropolitan statistical area/micropolitan statistical area'  # (320)


class ExtractStep(PipelineStep):
    def run_step(self, prev, params):
        year = params['year']
        sumlevels = params['sumlevels']
        estimate = params['estimate']

        pipeline_config_path = params['pipeline_config_path']
        fetcher = Fetcher(pipeline_config_path)
        return fetcher.fetch(
            years=[year],
            sumlevels=[sumlevels],
            estimates=[estimate])


class TransformStep(PipelineStep):
    def run_step(self, prev, params):
        dfs = prev
        # temp, TODO remove
        pipeline_config = yaml.load(open(params['pipeline_config_path']))
        print(pipeline_config)
        cube_generator = CubeGenerator(
            pipeline_config=pipeline_config,
            cube_name=pipeline_config['name'],
            value_label=pipeline_config['acs_table']['value_label'],
            input_dfs=dfs,
            schema='acs')
        return cube_generator.run()


def run(params, **kwargs):
    BAMBOO_LIB_DIR = os.environ.get("BAMBOO_LIB_DIR")
    conn_path = os.path.join(BAMBOO_LIB_DIR, "example", "conns.yaml")
    connector = Connector.fetch("postgres-local", open(conn_path))
    pipeline_config_path = params.get("pipeline_config_path")
    config_obj = yaml.load(open(pipeline_config_path))
    step1 = ExtractStep()
    step2 = TransformStep()
    step3 = LoadStep(config_obj["name"], connector, schema="acs")

    pipeline = LinearPipelineExecutor([step1, step2, step3], params)
    pipeline.run_pipeline()


if __name__ == '__main__':
    BAMBOO_LIB_DIR = os.environ.get("BAMBOO_LIB_DIR")
    run({"year": 2012,
         "estimate": 1,
         "sumlevels": "zip code tabulation area",
         "write-to-db": True,
         "pipeline_config_path": os.path.join(BAMBOO_LIB_DIR, "bamboo_lib/pipelines/bamboo_acs_pipeline/config/sex_by_age.yaml")})
