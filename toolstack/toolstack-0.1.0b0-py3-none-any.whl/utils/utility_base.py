import pandas as pd


def available_datasets():
    """
    List of available datasets
    """
    return([
        'Salary',
        'Weather'
    ])


def load_dataset(data):
    """
    Load the data from available datasets
    Parameters
    ----------
    data : Dataset Name
        The list of datasets can be found calling the utils.available_datasets()
    Returns
    -------
    DataFrame
    """
    return(pd.read_csv('https://raw.githubusercontent.com/getmykhan/toolstack/master/Datasets/'+ data +'.csv'))


def load_stopwords():
    """
    Default set of stopwords

    Returns
    -------
    Set
    """

    return set(pd.read_csv('https://algs4.cs.princeton.edu/35applications/stopwords.txt', header=-1)[0].values.tolist())
