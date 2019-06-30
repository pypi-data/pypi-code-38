import os
import pickle
import shutil
from auto_tqdm import tqdm
from typing import List, Callable

def get_desc(level: int):
    if level == 0:
        return "Holdouts"
    if level == 1:
        return "Inner holdouts"
    if level > 1:
        return "Inner holdouts (level {level})".format(level=level)


def is_cached(path: str)->bool:
    return os.path.exists(path)

def load_cache(path: str):
    with open("{path}.pickle".format(path=path), "rb") as f:
        return pickle.load(f)

def load(path: str, cache: bool, generator: Callable, dataset: List):
    if cache and is_cached(path):
        return load_cache(path)
    data = generator(dataset)
    return data[::2], data[1::2]


def store_cache(my_object, path: str):
    os.makedirs(path, exist_ok=True)
    with open("{path}.pickle".format(path=path), "wb") as f:
        pickle.dump(my_object, f)

def store(path: str, cache: bool, my_object):
    if cache and not is_cached(path):
        store_cache(my_object, path)


def holdouts_generator(*dataset: List, holdouts: List, verbose: bool = True, cache: bool = False, cache_dir: str = ".holdouts", level: int = 0):
    """Return validation dataset and another holdout generator
        dataset, iterable of datasets to generate holdouts from.
        holdouts:List, list of holdouts callbacks.
        verbose:bool=True, whetever to show or not loading bars.
        cache:bool=False, whetever to cache or not the rendered holdouts.
        cache_dir:str=".cache", directory where to cache the holdouts.
    """
    if holdouts is None:
        return None

    def generator():
        for outer_holdout, name, inner_holdouts in tqdm(list(holdouts), verbose=verbose, desc=get_desc(level)):
            path = "{cache_dir}/{name}".format(cache_dir=cache_dir, name=name)
            training, testing = load(
                path, cache, outer_holdout, dataset)
            store(path, cache, (training, testing))
            yield (training, testing), holdouts_generator(
                *training,
                holdouts=inner_holdouts,
                verbose=verbose,
                cache=cache,
                cache_dir=path,
                level=level+1
            )
    return generator

def clear_cache(cache_dir: str = ".holdouts"):
    """Remove the holdouts cache directory.
        cache_dir:str=".holdouts", the holdouts cache directory to be removed.
    """
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
