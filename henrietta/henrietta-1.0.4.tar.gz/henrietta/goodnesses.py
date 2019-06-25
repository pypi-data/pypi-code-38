import numpy as np

# for Python 2/3 compatibility
try:
    input = raw_input
except NameError:
    pass

def sumofsquares(residuals):
    '''
    This calculates a goodness-of-fit from an array of residuals.
    (a lower value implies a better fit)

    Parameters
    ----------
    residuals : `~numpy.ndarray`
        Array of values for (data-model)/sigma

    Returns
    -------
    gof : float
        A single goodness-of-fit metric
        (in this case, sum of squares)
    '''
    return np.sum(residuals**2)

def mean(residuals):
    '''
    This is a goodness-of-fit function. It calculate the mean
    of the residuals.

    Parameters
    ----------
    residuals : array
        Array of residuals = (data - model)/sigma

    Returns
    -------
    mean : float
        The mean of the residuals.
    '''

    return np.mean(residuals)

def chisq(residuals):
    '''
    This is a goodness-of-fit function. It calculates the sum of the squares
    of the residuals. This is commonly called "chi squared".

    Parameters
    ----------
    residuals : array
        Array of residuals = (data - model)/sigma

    Returns
    -------
    chisq : float
        The sum of the squared residuals.
    '''

    return np.sum(residuals**2)

def votes(residuals=None):
    '''
    This is a goodness-of-fit function. It averages votes
    from user input, and then spits out a 1-10 score.

    Returns
    -------
    averagevote : float
        The average of a bunch of user-entered votes.
    '''

    # get input from the user
    answer = input('On a scale of 1-10, how good is this model?\n[separate multiple entries by commas]\n')

    # convert a string into numbers, and return its average
    average = np.mean([float(x) for x in answer.split(',')])

    # return that average out of the function
    return average
