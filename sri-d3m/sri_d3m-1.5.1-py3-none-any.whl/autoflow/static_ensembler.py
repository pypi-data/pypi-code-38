import pandas
from typing import List
from sklearn.preprocessing import OneHotEncoder, LabelBinarizer
import numpy as np

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces.transformer import TransformerPrimitiveBase

from sri.common import config

Inputs = container.DataFrame
Outputs = container.DataFrame


class StaticEnsemblerHyperparams(meta_hyperparams.Hyperparams):
    # Weights assigned to constituent models
    weights = meta_hyperparams.Hyperparameter[List[float]](
        semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter'],
        default=[0.0, 0.0]
    )
    # Whether input from each model is a single value or a set of scores across classes
    scalar_input = meta_hyperparams.Hyperparameter[bool](
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        default=True
    )
    # Whether to produce scores for all classes or a single max value
    scalar_output = meta_hyperparams.Hyperparameter[bool](
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        default=True
    )
    # The number of classes in case of classification.  Use n<=1 to signal regression.
    class_count = meta_hyperparams.Hyperparameter[int](
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        default=2
    )


class StaticEnsembler(TransformerPrimitiveBase[Inputs, Outputs, StaticEnsemblerHyperparams]):
    """
Performs a linear transformation of input model predictions, based on the weights hyperparameter, with optional
maxarg selection in the case of classification.  This primitive serves to persist the determinations of some
ensembling operation that combines a number of atomic pipelines.  It does not perform ensembling itself and is
therefore not fittable.  It accepts a dataframe containing the predictions of its constituent pipelines, and produces
a dataframe with ensembled predictions.  The interpretation of both dataframes is controlled by hyperparameters
(see below).

It takes the following hyperparameters:

* **weights**: a list of real-valued weights over the constituent pipelines, one per pipeline, which record the
  relative importance of each.
* **scalar_input**: If true, the input contains one column per constituent pipeline, each element representing a
  categorical prediction.  If false, each constituent generates a dataframe as wide as the number of classes
  representing a probability distribution over the set of classes.  This hyperparameter is ignored for regression
  problems.
* **scalar_output**: Has an interpretation similar to scalar_input, but governs the structure of the dataframe
  produced by the primitive.  Again, it is ignored for regression problem, in which case there is always a single
  column of predictions.
* **class_count**: Stores the number of classes for categorical classification problems.  A value less than or
  equal to 1 signals a regression problem.
    """

    def __init__(self, *, hyperparams: StaticEnsemblerHyperparams) -> None:
        super().__init__(hyperparams=hyperparams)

    def produce(self, *, inputs: Inputs, timeout: float=None, iterations: int=None) -> pi_base.CallResult[Outputs]:
        """
        Perform a linear transform on inputs with possible maxarg output selection.
        """

        if isinstance(inputs, container.DataFrame) or isinstance(inputs, pandas.DataFrame):
            data = inputs
        else:
            data = inputs[0]

        class_count = self.hyperparams['class_count']
        weights = self.hyperparams['weights']
        weight_total = sum(weights)
        scalar_in = self.hyperparams['scalar_input']
        scalar_out = self.hyperparams['scalar_output']

        encoder = None
        if class_count > 1 and scalar_in:
            encoder = LabelBinarizer()
            encoder.fit(data.values.flatten())

        predictions = []

        for row in data.itertuples(index=False):
            assert len(row) == len(weights)
            if encoder is not None:
                row = encoder.transform(row)
            row = container.DataFrame(row).mul(weights, axis=0)
            prediction = row.sum() / weight_total
            # Classification
            if class_count > 1:
                if scalar_out:   # We want a single best prediction
                    prediction = prediction.idxmax(axis=1)
                    prediction = encoder.classes_[prediction]
                else:            # We want a distribution over classes
                    raise NotImplementedError()
            else:     # Regression
                raise NotImplementedError()
            predictions.append(prediction)

        return pi_base.CallResult(container.DataFrame(predictions))

    metadata = meta_base.PrimitiveMetadata({
        # Required
        "id": "ec24b04c-dbcc-11e8-9f8b-f2801f1b9fd1",
        "version": config.VERSION,
        "name": "Autoflow Static Ensembler",
        "description": """
            Performs a linear transformation of input model predictions, based on weight hyperparameter, with optional
            maxarg selection in the case of classification.
        """,
        "python_path": "d3m.primitives.data_transformation.conditioner.StaticEnsembler",
        "primitive_family": meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        "algorithm_types": [
            meta_base.PrimitiveAlgorithmType.ENSEMBLE_LEARNING
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'primitive', 'dataset', 'transformer' ],
        'installation': [ config.INSTALLATION ],
    })
