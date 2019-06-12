
import numpy
import pandas

def flatten (dictlist):
    """Flatten a list of dictionaries into a dictionary."""

    #if all (dictlist):
    results = {key : value for result in dictlist for key, value in result.items ()}

    return results

# convert dict with integer keys to numpy array - assume user plays nice
def numpify (dictionary):
    """Convert dict with integer keys to numpy array - assume user plays nice."""

    values = [dictionary [key] for key in range (len (dictionary))]
    return numpy.array (values)

# convert dict with integer keys and pandas DataFrame rows to pandas DataFrame - assume user plays nice
def pandify (dictionary):
    """Convert dict with integer keys and pandas DataFrame rows to pandas DataFrame - assume user plays nice."""

    auxiliary = isinstance (list (dictionary.values ()) [0], dict)
    if auxiliary:
        columns = list (list (dictionary.values ()) [0] ['scalars'] .index)
        scalars = {key : value ['scalars'] for key, value in dictionary.items ()}
    else:
        columns = list (list (dictionary.values ()) [0] .index)
        scalars = dictionary
    dataframe = pandas.DataFrame.from_dict (scalars, orient = 'index', columns = columns).sort_index ()
    if auxiliary:
        return {'scalars' : dataframe, 'auxiliary' : dictionary ['auxiliary']}
    else:
        return dataframe

def rounding (method):
    '''A decorator to map method arguments from float to integer by rounding.'''

    def mapped (value):
        return method ( (numpy.round (value)).astype(int) )
    return mapped

def logmeanstd (logm, logs):
    '''Return the needed quantities to construct stats.lognorm with a specified mean (logm) and standard deviation (logs).

    According to documentation at:
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html
    '''

    factor = 1 + (logs / logm) ** 2
    expm = logm / numpy.sqrt (factor)
    s = numpy.sqrt (numpy.log (factor))

    return { 's' : s, 'scale' : expm }