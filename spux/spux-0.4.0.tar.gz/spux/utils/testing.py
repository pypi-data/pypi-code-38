
import copy

from .seed import Seed
from .sandbox import Sandbox

def clone (model, parameters, time_clone, time_compare, inputset=None, sandbox=None, verbosity=1, seed=Seed()):
    """
    Test model cloning correctness (i.e., the save/load methods).

    1. Running the specified model to the specified *time_clone*.
    2. Clone model using save/load.
    3. Run both models to the specified *time_compare*.
    4. Compare the annotated results from both models.
    """

    if model.sandboxing and sandbox is None:
        print ('  : -> WARNING: No \'sandbox\' specified, but sandboxing is enabled for %s.' % model.name)
        print ('  : -> Setting sandbox to a default \'sandbox = Sandbox ()\'.')
        sandbox = Sandbox ()

    # set seed for the initial run until the clone time
    seed_clone = seed.spawn (0, name = 'clone')

    # run the first model up to the clone time and save its state
    print (' :: Running the model up to the specified clone time...')
    model1 = copy.deepcopy (model)
    sandbox1 = sandbox.spawn ('sandbox1') if sandbox is not None else None
    model1.isolate (sandbox1, verbosity)
    model1.plant (seed_clone)
    model1.init (inputset, parameters)
    prediction = model1.run (time_clone)
    print ('  : -> Obtained prediction at the clone time:')
    print (prediction)
    state = model1.save ()

    # clone the first model to the second model
    model2 = copy.deepcopy (model)
    sandbox2 = sandbox.spawn ('sandbox2') if sandbox is not None else None
    model2.isolate (sandbox2, verbosity)
    model2.load (state)

    # set seed for the following run until the compare time
    seed_compare = seed.spawn (1, name = 'compare')

    # plant and run both models up to the specified compare time
    print (' :: Running the original and the cloned models up to the specified compare time...')
    model1.plant (seed_compare)
    model2.plant (seed_compare)
    prediction1 = model1.run (time_compare)
    prediction2 = model2.run (time_compare)

    # compare predictions
    print ('  : -> Prediction of the original model (model1 in sandbox1):')
    print (prediction1)
    print ('  : -> Prediction of the cloned model (model2 in sandbox2):')
    print (prediction2)
    if all (prediction1 == prediction2):
        print (' :: SUCCESS: predictions of both models are identical.')
    else:
        print (' :: ERROR: predictions of both models are NOT identical.')
