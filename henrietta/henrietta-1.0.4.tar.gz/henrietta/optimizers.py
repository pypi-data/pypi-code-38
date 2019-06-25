import numpy as np

def guessncheck(objfunc, model, x, y, N=100):
    '''
    This function guesses and checks lots of different models,
    and returns the best oneself.

    Parameters
    ----------
    objfunc : function
        The function that tells us how good a fit is, based on the model
        and the data (this is fed automitically by our "fitter").

    model : astropy.model
        The astropy model we're trying to fit.

    x : numpy.ndarray
        The independent values (x).

    y : numpy.ndarray
        The dependent values (y).

    N : int
        How many models should we try?
    '''

    # assume our first model has the best parameters (initially)
    best = model.parameters

    # create a tester model to play with
    tester = model.copy()

    # create an empty array for our goodness of fit
    gof = np.ones(N)*np.inf

    # do a bunch of iterations
    for i in range(N):

        # set the parameters, by drawing randomly from their bounds
        for w, p in enumerate(model.param_names):

            # only randomize bounded and un-fixed variables
            if None in model.bounds[p] or model.fixed[p]:
                pass
            else:
                tester.parameters[w] = np.random.uniform(*model.bounds[p])

        # calculate the goodness of fit
        gof[i] = objfunc(measured_vals=y,
                         updated_model=tester,
                         weights=None,
                         x=x)

        # store the best set of parameters
        if gof[i] <= np.nanmin(gof):
            best = tester.parameters

    return best
