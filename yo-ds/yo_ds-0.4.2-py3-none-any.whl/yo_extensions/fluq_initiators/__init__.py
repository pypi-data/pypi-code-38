from yo_core import *
from pathlib import Path
import itertools, gzip, pickle
import os

def _grid_iter(keys,lists):
    for config in itertools.product(*lists):
        yield Obj(**{key: value for key, value in zip(keys, config)})

def _grid(**kwargs):
    keys = list(kwargs)
    lists = [kwargs[key] for key in keys]
    length = 1
    for l in lists:
        length*=len(l)
    return Queryable(_grid_iter(keys, lists), length)


def _grid_args(args):
    length = 1
    for l in args:
        length*=len(l)
    return Queryable(itertools.product(*args),length)



def _triangle_iter(items,with_diagonal):
    for index1,item1 in enumerate(items):
        begin = index1
        if not with_diagonal:
            begin+=1
        for index2 in range(begin,len(items)):
            item2=items[index2]
            yield (item1,item2)




def _text_file(filename, **kwargs):
    with open(filename, 'r', **kwargs) as file:
        for line in file:
            if line.endswith('\n'):
                line = line[:-1]
            yield line

def _zip_text_file(filename, encoding):
    with gzip.open(filename, 'rb') as f:
        for line in f:
            if line.endswith(b'\n'):
                line = line[:-1]
            yield line.decode(encoding)


def _pickle_file(filename):
    with open(filename, 'rb') as file:
        while file.read(1):
            file.seek(-1, 1)
            length = file.read(4)
            length = int.from_bytes(length, 'big')
            dump = file.read(length)
            obj = pickle.loads(dump)
            yield obj



def folder(location: Union[Path, str], pattern: Optional[str] = None):
    if isinstance(location,str):
        location = Path(location)
    elif isinstance(location,Path):
        pass
    else:
        raise ValueError('Location should be either str or Path, but was {0}, {1}'.format(type(location),location))

    if not os.path.isdir(location):
        raise ValueError('{0} is not a directory'.format(location))

    return location.glob(pattern)


class FileQuery:
    def text(self, path: Union[str,Path], **file_kwargs) -> Queryable[str]:
        return Queryable(_text_file(path, **file_kwargs))

    def zipped_text(self, path: Union[str,Path], encoding: str ='utf-8') -> Queryable[str]:
        return Queryable(_zip_text_file(path, encoding))

    def pickle(self, path: Union[str,Path]) -> Queryable[Any]:
        return Queryable(_pickle_file(path))



T = TypeVar('T')

from itertools import combinations

class CombinatoricsQuery:
    def grid(self, **kwargs)->Queryable[Obj]:
        return _grid(**kwargs)

    def cartesian(self,*args)->Queryable[Tuple]:
        return _grid_args(args)

    def triangle(self, items: T, with_diagonal=True) -> Queryable[Tuple[T, T]]:
        return Queryable(_triangle_iter(items, with_diagonal), (len(items) * (len(items) - 1)) // 2)

    def powerset(self, iterable: Iterable[T]) -> Queryable[Tuple]:
        xs = list(iterable)
        return Query.en(range(len(xs) + 1)).select_many(lambda z: combinations(xs, z))