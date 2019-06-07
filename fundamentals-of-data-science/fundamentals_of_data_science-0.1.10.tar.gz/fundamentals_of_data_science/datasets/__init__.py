import os
import pandas as pd


def imports_85():
    """
    Returns the imports-85 dataset.

    Usage
    -----
        >>> import fundamentals_of_data_science as fun
        >>> df = fun.datasets.imports_85()
        >>> df.head()
    """
    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'imports-85.data.csv'))
    return(pd.read_csv(filename))


def kc_house_data():
    """
    Returns the kc_house_data dataset.

    Usage
    -----
        >>> import fundamentals_of_data_science as fun
        >>> df = fun.datasets.kc_house_data()
        >>> df.head()
    """
    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'kc_house_data.csv'))
    return(pd.read_csv(filename))


def arsenic():
    """
    Returns the arsenic dataset.

    Usage
    -----
        >>> import fundamentals_of_data_science as fun
        >>> df = fun.datasets.arsenic()
        >>> df.head()
    """
    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'arsenic.wells.tsv'))
    return(pd.read_csv(filename, delimeter="\t"))


def child_iq():
    """
    Returns the child_iq dataset.

    Usage
    -----
        >>> import fundamentals_of_data_science as fun
        >>> df = fun.datasets.child_iq()
        >>> df.head()
    """
    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'child_iq.tsv'))
    return(pd.read_csv(filename, delimeter="\t"))        


def mesquite():
    """
    Returns the mesquite dataset.

    Usage
    -----
        >>> import fundamentals_of_data_science as fun
        >>> df = fun.datasets.mesquite()
        >>> df.head()
    """
    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mesquite.tsv'))
    return(pd.read_csv(filename, delimeter="\t"))                