"""
A collection of convenient methods when working with dicts
"""
from collections import defaultdict
from typing import Any, Dict, TypeVar, Callable, Iterable, Hashable, List

# 'Recursive types not fully supported yet, nested types replaced with "Any"'
TreeT = Dict[str, Any]

DEFAULT_SEP = '/'


def inflate(deflated, sep=DEFAULT_SEP):
    # type: (Dict[str, Any], str) -> TreeT
    """
    Interpret the keys as paths in a tree to its leaf nodes, the values as the
    corresponding value and return a nested dict representation of that tree.

    **Keys without sep are not inflated**

        >>> inflate({'aix': 13})
        {'aix': 13}

    **Keys with sep produce nested dict**

        >>> inflate({'a/i/x': 13})
        {'a': {'i': {'x': 13}}}

    **Children can be internal nodes and leaf nodes both**

        >>> (inflate({'a/i/x': 13, 'a/j': 17})
        ... == {'a': {'i': {'x': 13}, 'j': 17}})
        True

    **Only leaf nodes can have values**

        >>> from collections import OrderedDict
        >>> inflate(OrderedDict([('a/i', 13), ('a', 17)]))
        Traceback (most recent call last):
        ...
        RuntimeError: Internal node must not be assigned a value.

        >>> inflate(OrderedDict([('a', 13), ('a/i', 17)]))
        Traceback (most recent call last):
        ...
        RuntimeError: Leaf node must not be assigned children.

    **Every leaf node must have a value**

        >>> inflate({'a': {}})
        Traceback (most recent call last):
        ...
        TypeError: Value must not be another dict

    **Input must be flat**

        >>> inflate({'a': {'i': 13}})
        Traceback (most recent call last):
        ...
        TypeError: Value must not be another dict

    **Dicts inside non-dict objects are ignored**

        >>> (inflate({'a/i': ({'x': 13},)})
        ... == {'a': {'i': ({'x': 13},)}})
        True

    **Leaves input unchanged**

        >>> d = {'a/i/x': 13, 'a/j': 17}
        >>> i = inflate(d)
        >>> d == {'a/i/x': 13, 'a/j': 17}
        True

    **Input and output are untangled**

        >>> d['foo'] = 19; 'foo' in i
        False
        >>> i['bar'] = 23; 'bar' in d
        False


    **Keys must be unicode**

        >>> inflate({b'1': 13})
        Traceback (most recent call last):
        ...
        TypeError: Key must be a string

    """
    ret = {}  # type: TreeT
    for key, value in deflated.items():
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        if isinstance(value, dict):
            raise TypeError("Value must not be another dict")
        _set(ret, key.split(sep), value)
    return ret


def _set(tree, path, value):
    if len(path) == 1:
        head = path[0]
        if head in tree and isinstance(tree[head], dict):
            raise RuntimeError("Internal node must not be assigned a value.")
        tree[head] = value
    else:
        head, tail = path[0], path[1:]
        if head not in tree:
            tree[head] = {}
        elif not isinstance(tree[head], dict):
            raise RuntimeError("Leaf node must not be assigned children.")
        _set(tree[head], tail, value)


def deflate(inflated, sep=DEFAULT_SEP):
    # type: (TreeT, str) -> Dict[str, Any]
    """
    Walk the tree provided as a nested dict and for every leaf node add its
    path and value as a key: value mapping in the returned dictionary.

    **Trees of depth one produce themselves**

        >>> deflate({'a': 13})
        {'a': 13}

    **Deep trees produce long paths**

        >>> deflate({'a': {'i': {'x': 13}}})
        {'a/i/x': 13}

    **Children can be internal nodes and leaf nodes both**

        >>> (deflate({'a': {'i': {'x': 13}, 'j': 17}})
        ... == {'a/i/x': 13, 'a/j': 17})
        True

    **Every leaf node must have a value**

        >>> deflate({'a': {}})
        Traceback (most recent call last):
        ...
        ValueError: Nodes must have at least one child or a value


    **Keys must not contain sep**

        >>> deflate({'a': {'i': 13}, 'a/i': 17})
        Traceback (most recent call last):
        ...
        ValueError: Key must not contain path separator

    **Dicts inside non-dict objects are ignored**

        >>> (deflate({'a': {'i': ({'x': 13},)}})
        ... == {'a/i': ({'x': 13},)})
        True

    **Leaves input unchanged**

        >>> i = {'a': {'i': {'x': 13}, 'j': 17}}
        >>> d = deflate(i)
        >>> i == {'a': {'i': {'x': 13}, 'j': 17}}
        True


    **Input and output are untangled**

        >>> i['bar'] = 23; 'bar' in d
        False
        >>> d['foo'] = 19; 'foo' in i
        False


    **Keys must be strings**

        >>> deflate({b'1': 13})
        Traceback (most recent call last):
        ...
        TypeError: Key must be a string

    **Lists are left intact by default**

        >>> deflate({'a': [13, {'i': 17}]})
        {'a': [13, {'i': 17}]}

    """
    return {sep.join(path): value for path, value in _walk(inflated, (), sep)}


def _walk(tree, root, sep):
    if not tree:
        raise ValueError("Nodes must have at least one child or a value")

    for key, value in tree.items():
        if not isinstance(key, str):
            raise TypeError("Key must be a string")

        if sep in key:
            raise ValueError("Key must not contain path separator")

        path = root + (key, )

        if isinstance(value, dict):
            yield from _walk(value, path, sep)
        else:
            yield path, value


T = TypeVar("T")
V = TypeVar("V", bound=Hashable)


def group_by(
        iterable: Iterable[T],
        keyfunc: Callable[[T], V],
) -> Dict[V, List[T]]:
    """Group items by key

    Similar to `itertools.groupby` except
    * consumes input eagerly,
    * order of input does not matter,
    * returned type is different.
    """
    result = defaultdict(list)  # type:Dict[V, List[T]]
    for value in iterable:
        key = keyfunc(value)
        result[key].append(value)
    return result


def invert(mapping: Dict[T, V]) -> Dict[V, T]:
    """Invert dictionary

    Trivial function but good for two reasons:
    * it gives the operation a name, and
    * it catches an edge case that is easily forgotten.
    """
    result = {v: k for (k, v) in mapping.items()}  # type: Dict[V, T]
    if len(result) != len(mapping):
        raise ValueError("Duplicate values in mapping")
    return result
