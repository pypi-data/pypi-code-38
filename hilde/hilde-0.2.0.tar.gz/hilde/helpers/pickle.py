""" Pickle a python object and save it as a compressed file """

import pickle
import gzip
from pathlib import Path


def psave(obj, oname="test.pick", compressed=True, verbose=False):
    """ save as (compressed) pickled file """
    if compressed:
        oname = str(oname) + ".gz"
        with gzip.open(oname, "wb", 5) as f:
            pickle.dump(obj, f)
    else:
        with open(oname, "wb") as f:
            pickle.dump(obj, f)
    #
    if verbose:
        print(f"List of {len(obj)} objects written to {oname}.")


def pread(fname):
    """ read (compressed) pickled file """
    if "gz" in Path(fname).suffix:
        with gzip.open(fname, "rb") as f:
            return pickle.load(f)
    with open(fname, "rb") as f:
        return pickle.load(f)
