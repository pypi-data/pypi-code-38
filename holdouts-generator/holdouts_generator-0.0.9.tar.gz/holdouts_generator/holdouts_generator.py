import os
import pickle
import shutil
from auto_tqdm import tqdm
from typing import List, Callable

___holdouts_memory_cache___ = {}

class ConstError(TypeError): pass
class MemoryHoldoutsModifiedError(ConstError): pass

def get_desc(level:int):
    if level==0:
        return "Holdouts"
    if level==1:
        return "Inner holdouts"
    if level>1:
        return "Inner holdouts (level {level})".format(level=level)

def is_cached(path:str)->bool:
    return os.path.exists(path)

def is_memory_cached(path:str)->bool:
    global ___holdouts_memory_cache___
    return path in ___holdouts_memory_cache___

def load_cache(path:str):
    with open("{path}.pickle".format(path=path), "rb") as f:
        return pickle.load(f)

def load_memory_cache(path:str):
    global ___holdouts_memory_cache___
    return ___holdouts_memory_cache___[path]

def load(path:str, cache:bool, memory_cache:bool, generator:Callable, dataset:List):
    if memory_cache and is_memory_cached(path):
        return load_memory_cache(path)
    if cache and is_cached(path):
        return load_cache(path)
    return generator(dataset)

def store_cache(my_object, path:str):
    os.makedirs(path, exist_ok=True)
    with open("{path}.pickle".format(path=path), "wb") as f:
        pickle.dump(my_object, f)

def store_memory_cache(my_object, path:str):
    global ___holdouts_memory_cache___
    ___holdouts_memory_cache___[path] = my_object

def store(path:str, cache:bool, memory_cache:bool, my_object):
    if memory_cache and not is_memory_cached(path):
        store_memory_cache(my_object, path)
    if cache and not is_cached(path):
        store_cache(my_object, path)

def holdouts_generator(*dataset:List, holdouts:List, verbose:bool=True, cache:bool=False, memory_cache:bool=False, cache_dir:str=".holdouts", level:int=0):
    """Return validation dataset and another holdout generator
        dataset, iterable of datasets to generate holdouts from.
        holdouts:List, list of holdouts callbacks.
        verbose:bool=True, whetever to show or not loading bars.
        cache:bool=False, whetever to cache or not the rendered holdouts.
        memory_cache:bool=False, whetever to keep the object in memory.
        cache_dir:str=".cache", directory where to cache the holdouts.
    """
    if holdouts is None:
        return None
    def generator():
        for outer_holdout, name, inner_holdouts in tqdm(list(holdouts), verbose=verbose, desc=get_desc(level)):
            path = "{cache_dir}/{name}".format(cache_dir=cache_dir, name=name)
            validation = load(path, cache, memory_cache, outer_holdout, dataset)
            store(path, cache, memory_cache, validation)
            training, testing = validation[::2], validation[1::2]
            yield (training, testing), holdouts_generator(
                *training,
                holdouts=inner_holdouts,
                verbose=verbose,
                cache=cache,
                memory_cache=memory_cache,
                cache_dir=path,
                level=level+1
            )
    return generator

def clear_memory_cache():
    """Remove the holdouts memory cache."""
    global ___holdouts_memory_cache___
    for key in list(___holdouts_memory_cache___.keys()):
        del ___holdouts_memory_cache___[key]
    ___holdouts_memory_cache___ = {}

def clear_cache(cache_dir:str=".holdouts"):
    """Remove the holdouts cache directory.
        cache_dir:str=".holdouts", the holdouts cache directory to be removed.
    """
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)