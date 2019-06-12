
import numpy
import pandas
import os

from .seed import Seed
from ..io import dumper

def generate (model, parameters, times, error=None, replicates=None, inputsets=None, sandbox=None, verbosity=1, seed=Seed(), outputdir='datasets'):
    """
    Generate a synthetic dataset (or multiple datasets if replicates is set) for the specified model and parameters.

    Two sets of files are generated for each time specified by *times*:
     - predictions*.dat: exact model predictions to be used as a reference for comparison with the maximum a posteriori (MAP) estimante,
     - dataset*.dat: model predictions perturbed by the specified error model (only if the error model is specified).

    If *replicates* is specified (non-negative integer), multiple stochastic realizations are generated.
    """

    rng = numpy.random.RandomState (seed ())

    if error is None:
        print (" ::WARNING: Error model is not specified, dataset*.dat will be identical to predictions*.dat.")

    dumper.mkdir (outputdir, fresh = True)

    def observe (prediction):
        if error is not None:
            # if hasattr (error, 'transform'):
            #     prediction = error.transform (prediction, parameters)
            observation = error.distribution (prediction, parameters) .draw (rng)
            if isinstance (prediction, dict):
                observation = observation ['scalars']
            observation.name = prediction.name
        else:
            observation = prediction
        return observation

    for replicate in range (0, replicates if replicates is not None else 1):

        model.isolate (sandbox, verbosity)
        seed_replicate = seed.spawn (replicate)
        model.plant (seed_replicate)
        inputset = inputsets [replicate] if inputsets is not None else None
        model.init (inputset, parameters)

        model.plant (seed_replicate.spawn (0))
        prediction = model.run (times [0])
        if isinstance (prediction, dict):
            predictions = pandas.DataFrame (prediction ['scalars']).T
        else:
            predictions = pandas.DataFrame (prediction).T
        dataset = pandas.DataFrame (observe (prediction)).T

        for iteration, time in enumerate (times [1:]):

            model.plant (seed_replicate.spawn (iteration + 1))
            prediction = model.run (time)
            predictions.loc [time] = prediction
            dataset.loc [time] = observe (prediction)

        suffix = ('_%s' % replicate) if replicates is not None else ''
        predictions.index.name = 'time'
        dataset.index.name = 'time'
        predictions.to_csv (os.path.join (outputdir, 'predictions%s.dat' % suffix))
        dataset.to_csv (os.path.join (outputdir, 'dataset%s.dat' % suffix))