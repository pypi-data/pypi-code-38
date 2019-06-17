from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline

import sri.pipelines.datasets as datasets
from sri.pipelines.base import BasePipeline
from sri.psl.general_relational_dataset import GeneralRelationalDataset

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
    # The following cause pipelines to fail when calling out to the PSL jar - see D3M-205
    '60_jester',
    '1567_poker_hand',
    '6_70_com_amazon',
    # Broken for various reasons
    '32_wikiqa',
    'uu3_world_development_indicators',
    '26_radon_seed',
    '22_handgeometry',
    'SEMI_155_pokerhand',
    'uu7_pima_diabetes',
    '66_chlorineConcentration',
    'uu6_hepatitis',
    'uu5_heartstatlog',
    'uu3_world_development_indicators_raw',
    'LL1_bn_fly_drosophila_medulla_net',
    'LL1_multilearn_emotions',
    'LL0_207_autoPrice',
    '534_cps_85_wages',
    '196_autoMpg',
}

class GeneralRelationalDatasetPipeline(BasePipeline):
    def __init__(self):
        super().__init__(set(datasets.get_dataset_names()) - SKIP_DATASETS, True)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = GeneralRelationalDataset.metadata.query())
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
