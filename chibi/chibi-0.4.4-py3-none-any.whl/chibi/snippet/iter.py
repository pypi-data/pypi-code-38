import itertools


def chunks( iterable, size=1000 ):
    """
    Make digestible chunks of something that can be iterated

    Arguments
    ---------
    iterable: list, tuple, generator
        Just have to support the iter function will break it
        in digestible chunks
    size: size of the digestibles chunks

    Examples
    --------
    >>> [ list( chunk ) for chunk in chunks( range( 10 ), size=5 ) ]
    [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
    """
    iterator = iter( iterable )
    for i in iterator:
        yield itertools.chain( [i], itertools.islice( iterator, size - 1 ) )


class ___DUMP:
    def __init__( self, dump ):
        self.dump = dump


def chunk_each( l, f ):
    inner_result = []
    result = []
    iterator = iter( l )
    for i in iterator:
        if f( i ):
            if inner_result:
                result.append( inner_result )
            inner_result = []
        inner_result.append( i )
    if inner_result:
        result.append( inner_result )
    return result


def cut_until( iterator, until ):
    for i in iterator:
        if until( i ):
            break
        yield i
