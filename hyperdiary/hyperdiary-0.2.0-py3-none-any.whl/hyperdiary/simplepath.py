from typing import Iterable, List

class InvalidPathError(Exception):
    pass

class NotARelativePathError(InvalidPathError):
    pass

class NotAnAbsolutePathError(InvalidPathError):
    pass

_valid_path_chars = 'abcdefghijklmnopqrstuvwxyz0123456789-_.'
def _validate_and_shorten(is_absolute: bool, elements: Iterable[str]) -> List[str]:
    '''
    >>> _validate_and_shorten(True, ['a', 'b', 'c', '..', '..'])
    ['a']

    >>> _validate_and_shorten(False, ['..', '..'])
    ['..', '..']

    >>> _validate_and_shorten(True, ['..', '..'])
    Traceback (most recent call last):
        ...
    hyperdiary.simplepath.InvalidPathError: traversing over root

    >>> _validate_and_shorten(True, ['x', '..'])
    []
    >>> _validate_and_shorten(False, ['x', '..'])
    []

    >>> _validate_and_shorten(True, [''])
    []
    >>> _validate_and_shorten(True, [])
    []
    >>> _validate_and_shorten(False, ['.'])
    []
    >>> _validate_and_shorten(False, [''])
    []
    >>> _validate_and_shorten(False, [])
    []
    >>> _validate_and_shorten(False, ['.'])
    []
    '''
    new_elements = [] # type: List[str]
    for el in elements:
        if el == '.' or not el:
            continue
        elif el == '..':
            if not new_elements:
                if is_absolute:
                    raise InvalidPathError('traversing over root')
                else:
                    new_elements.append('..')
            else:
                if new_elements[-1] == '..':
                    new_elements.append('..')
                else:
                    new_elements.pop()
        else:
            if not all(c in _valid_path_chars for c in el):
                raise InvalidPathError('invalid character in path element "{}"'.format(el))
            new_elements.append(el)
    return new_elements

class RelativePath:
    def __init__(self, path: str) -> None:
        '''
        >>> RelativePath('a/b/c')
        RelativePath('./a/b/c')

        >>> RelativePath('..')
        RelativePath('..')

        >>> RelativePath('.')
        RelativePath('.')

        >>> RelativePath('')
        RelativePath('.')
        '''
        if path.startswith('/'):
            raise NotARelativePathError(path)
        self.elements = _validate_and_shorten(False, path.split('/'))

    def __str__(self):
        '''
        >>> str(RelativePath('a/b/c'))
        './a/b/c'
        '''
        prefix = '.' + ('/' if self.elements else '')
        if self.elements and self.elements[0] == '..':
            prefix = ''
        return prefix + '/'.join(self.elements)

    def __repr__(self):
        '''
        >>> RelativePath('d/e/f')
        RelativePath('./d/e/f')

        >>> RelativePath('./../f')
        RelativePath('../f')
        '''
        return 'RelativePath(\'{}\')'.format(self)


class AbsolutePath:
    def __init__(self, path: str) -> None:
        '''
        >>> AbsolutePath('/a/b/c')
        AbsolutePath('/a/b/c')

        >>> AbsolutePath('/')
        AbsolutePath('/')

        >>> AbsolutePath('/folder/index.html')
        AbsolutePath('/folder/index.html')

        >>> AbsolutePath('a/b/c')
        Traceback (most recent call last):
            ...
        hyperdiary.simplepath.NotAnAbsolutePathError: a/b/c

        >>> AbsolutePath('')
        Traceback (most recent call last):
            ...
        hyperdiary.simplepath.NotAnAbsolutePathError
        '''
        if not path.startswith('/'):
            raise NotAnAbsolutePathError(path)
        self.elements = _validate_and_shorten(True, path.split('/'))

    def __eq__(self, other: object) -> bool:
        '''
        >>> AbsolutePath('/a/b/c') == AbsolutePath('/a/b/c')
        True

        >>> AbsolutePath('/a/b/c') == AbsolutePath('/a/./b/c/../c')
        True

        >>> AbsolutePath('/a/b/c') == AbsolutePath('/a')
        False

        >>> AbsolutePath('/a/b/c') != AbsolutePath('/a')
        True
        '''
        if not isinstance(other, AbsolutePath):
            return False
        if not len(self.elements) == len(other.elements):
            return False
        return all(el1 == el2 for el1, el2 in zip(self.elements, other.elements))

    def __add__(self, other: RelativePath) -> 'AbsolutePath':
        '''
        >>> AbsolutePath('/a/b/c') + RelativePath('d/e/f')
        AbsolutePath('/a/b/c/d/e/f')

        >>> AbsolutePath('/a/b/c') + RelativePath('../..')
        AbsolutePath('/a')

        >>> AbsolutePath('/a/b/c') + RelativePath('../../..')
        AbsolutePath('/')

        >>> AbsolutePath('/a/b/c') + RelativePath('../../../..')
        Traceback (most recent call last):
            ...
        hyperdiary.simplepath.InvalidPathError: traversing over root

        >>> AbsolutePath('/a/b/c/././') + RelativePath('../../../x/y') == AbsolutePath('/x/y')
        True
        '''
        return AbsolutePath('{}/{}'.format(self, other))

    def __sub__(self, other: 'AbsolutePath') -> RelativePath:
        '''
        >>> AbsolutePath('/a/b/c') - AbsolutePath('/a/b/c')
        RelativePath('.')

        >>> AbsolutePath('/a/b/c') - AbsolutePath('/a/b/x')
        RelativePath('../c')

        >>> AbsolutePath('/a/b/c') - AbsolutePath('/d/e/f')
        RelativePath('../../../a/b/c')

        >>> a = AbsolutePath('/a/b/c'); b = AbsolutePath('/a/x/y')
        >>> b + (a - b) == a
        True
        >>> a + (b - a) == b
        True
        '''
        e1 = self.elements.copy()
        e2 = other.elements.copy()
        while e1 and e2 and e1[0] == e2[0]:
            e1.pop(0)
            e2.pop(0)
        return RelativePath('../' * len(e2) + '/'.join(e1))

    def __str__(self):
        '''
        >>> str(AbsolutePath('/a/b/c'))
        '/a/b/c'
        '''
        return '/' + '/'.join(self.elements)

    def __repr__(self):
        '''
        >>> AbsolutePath('/a/b/c')
        AbsolutePath('/a/b/c')
        '''
        return 'AbsolutePath(\'{}\')'.format(self)

    def __hash__(self):
        return hash(repr(self))
