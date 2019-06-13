import abc
import json
import os
import re
import tempfile

from d3m.metadata.base import ArgumentType
from d3m.metadata.pipeline import PrimitiveStep

import sri.pipelines.datasets as datasets
from sri.common import constants

# If the NIST testing executable is available, then we will try to evaluate predictions with it.
try:
    import d3m_outputs
    EVAL_PREDICTIONS = True
except ImportError:
    EVAL_PREDICTIONS = False

PREDICTIONS_PATH = os.path.join(tempfile.gettempdir(), 'test_predictions.csv')

ATTR_TYPE = "https://metadata.datadrivendiscovery.org/types/Attribute"
TARG_TYPE = "https://metadata.datadrivendiscovery.org/types/TrueTarget"

class BasePipeline(object):

    # Prediction pipelines are epcected to go all the way and end with a single dataframe.
    def __init__(self, datasets, prediction_pipeline):
        self._datasets = datasets
        self._prediction_pipeline = prediction_pipeline
        self._pipeline = self._gen_pipeline()

    @abc.abstractmethod
    def _gen_pipeline(self):
        '''
        Create a D3M pipeline for this class.
        '''
        pass

    def assert_result(self, tester, results, dataset, score_dir):
        '''
        Make sure that the results from an invocation of this pipeline are valid.
        Children should override if they have more details.
        '''

        # The results are always nested.
        tester.assertEquals(len(results), 1)

        result_frame = results['outputs.0']

        # Prediction pipelines should always have a d3m index and give the correct number of rows.
        if (self._prediction_pipeline):
            tester.assertTrue(constants.D3M_INDEX in result_frame.columns)
            tester.assertEquals(len(result_frame), datasets.get_size(dataset))

            if (EVAL_PREDICTIONS):
                self._eval_predictions(tester, result_frame, score_dir)

    def is_prediction_pipeline(self):
        return self._prediction_pipeline

    def get_id(self):
        return self._pipeline.id

    def get_datasets(self):
        '''
        Get the name of datasets compatibile with this pipeline.
        '''
        return self._datasets

    def get_json(self):
        json_obj = self._pipeline.to_json()
        json_string = json.loads(json_obj)

        # Make it pretty.
        json_dump = json.dumps(json_string, indent = 4)

        # Purge any digest information to prevent validation failure
        return re.sub(',*\s*\"digest\" *: *\".*\"(,|(?=\s+\}))', '', json_dump)

    def _eval_predictions(self, tester, predictions, score_dir):
        predictions.to_csv(PREDICTIONS_PATH, index = False)

        nist_predictions = d3m_outputs.Predictions(PREDICTIONS_PATH, score_dir)
        tester.assertTrue(nist_predictions.is_valid())

        targets_path = os.path.join(score_dir, 'targets.csv')
        scores = nist_predictions.score(targets_path)
        tester.assertIsNotNone(scores)

    # Convenience function to enable less verbose construction of pipelines in subclasses
    def _add_pipeline_step(self, pipeline, prim, **args):
        pclass = type(prim)
        mdata = pclass.metadata.query()
        pstep = PrimitiveStep(primitive_description=mdata)
        pargs = mdata['primitive_code'].get('arguments', {})

        for arg, node in args.items():
            if pargs.get(arg, None) is not None:
                pstep.add_argument(arg, ArgumentType.CONTAINER, node)
        pstep.add_output("produce")

        for hp, val in prim.hyperparams.items():
            pstep.add_hyperparameter(name=hp, argument_type=ArgumentType.VALUE, data=val)
        pipeline.add_step(pstep)

        return "steps.%d.produce" % (len(pipeline.steps) - 1)
