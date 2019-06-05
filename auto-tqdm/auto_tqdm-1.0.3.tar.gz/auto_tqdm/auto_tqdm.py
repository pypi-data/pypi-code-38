from tqdm import tqdm_notebook, tqdm as tqdm_cli
from environments_utils import is_notebook
from typing import Dict, Generator


def tqdm(iterable=None, verbose: bool = True, **kwargs: Dict)->Generator:
    """Return adaptative tqdm given the identified environment.
        iterable, object to iterate over.
        verbose:bool, whetever to show the bar or not.
        kwargs:Dict, parameters to pass to the tqdm object.
    """
    if not verbose and iterable is not None:
        return (i for i in iterable)

    return (tqdm_notebook if is_notebook() else tqdm_cli)(iterable, **kwargs)