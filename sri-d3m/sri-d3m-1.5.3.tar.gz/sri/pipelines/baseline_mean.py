from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline

import sri.pipelines.datasets as datasets
from sri.baseline.mean import MeanBaseline
from sri.pipelines.base import BasePipeline

# These datasets are irregular.
SKIP_DATASETS = {
    # https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/105
    '1491_one_hundred_plants_margin_clust',
    # https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/104
    'DS01876',
    # Two target columns.
    'uu2_gp_hyperparameter_estimation',
    'uu2_gp_hyperparameter_estimation_v2',
    'LL1_penn_fudan_pedestrian',
    # Generates out of range score which causes pipeline output to fail validation
    '6_86_com_DBLP',
    # The following fail for a variety of reasons
    'uu6_hepatitis',
    '32_wikiqa',
    'uu5_heartstatlog',
    'LL1_bn_fly_drosophila_medulla_net',
    '534_cps_85_wages',
    '196_autoMpg',
    '26_radon_seed',
    'LL0_207_autoPrice',
    '22_handgeometry',
    'LL1_multilearn_emotions',
    'uu7_pima_diabetes',
    '60_jester',
}



class MeanBaselinePipeline(BasePipeline):

    CHALLENGE_PROBLEMS = ['LL0_acled_reduced', 'LL1_OSULeaf', 'LL1_TXT_CLS_airline_opinion',
                          'uu3_world_development_indicators']

    def __init__(self):
        problems = set(datasets.get_dataset_names()) - SKIP_DATASETS
        super().__init__(problems, True)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = MeanBaseline.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'results', data_reference = 'steps.0.produce')

        return pipeline
