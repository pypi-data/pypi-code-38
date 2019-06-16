#
#   Copyright EAVISE
#   Author: Maarten Vandersteegen
#   Author: Tanguy Ophoff
#
import os
from pathlib import Path
from ._util import expand
from .parser import ParserType, Parser, formats
from .. import util

__all__ = ['load', 'save']


def load(fmt, path, identify=None, offset=0, stride=1, **kwargs):
    """ Parse any type of bounding box format.

    Args:
        fmt (str or class or Parser): Format from the :ref:`brambox.io.formats <brambox.io.formats>` dictionary
        path (list or string): Bounding box filename or array of bounding box filenames
        identify (function, optional): Function to create a file identifier
        offset (int, optional): Skip images untill offset; Default **0**
        stride (int, optional): Only read every n'th file; Default **1**
        **kwargs: Keyword arguments that are passed to the parser

    Returns:
        pandas.DataFrame: Dataframe containing the bounding boxes for every image

    Note:
        The ``identify`` function gets used to generate some kind of ``file_id`` tag
        for each different file of :py:attr:`~brambox.io.parser.ParserType.MULTI_FILE` parsers. |br|
        Its input is the path to the file and as output it needs to generate some kind of ID tag.
        The default function will return the basename without extension.

        Most :py:attr:`~brambox.io.parser.ParserType.MULTI_FILE` parsers split the data into one file per image
        and thus require this ID to be the string for the image column.
        However, this can be different for some parsers, so check the `serialize_group` attribute of the individual parsers.

    Warning:
        The ``path`` parameter can be either a list or string. |br|
        If the format is of the type :py:attr:`~brambox.io.parser.ParserType.SINGLE_FILE`,
        then only a string is accepted and this is used as the filename. |br|
        If the format is of the type :py:attr:`~brambox.io.parser.ParserType.MULTI_FILE`,
        then you can either pass a list or a string.
        A list will be used as is, namely every string of the list gets used as a filename.
        If you use a string, it will first be expanded with the :func:`~brambox.io._util.expand` function
        to generate a list of strings. This expand function can take optional stride and offset parameters,
        which can be passed via keyword arguments.
    """
    # Create parser
    if type(fmt) is str:
        try:
            parser = formats[fmt](**kwargs)
        except KeyError as err:
            raise TypeError(f'Invalid parser {fmt}') from err
    elif isinstance(fmt, Parser):
        if len(kwargs) != 0:
            log.error(f'fmt argument is already an instantiated parser. Ignoring passed kwargs {kwargs}')
        parser = fmt
    elif issubclass(fmt, Parser):
        parser = fmt(**kwargs)
    else:
        raise TypeError(f'Invalid parser {fmt}')

    # Parse bounding boxes
    if parser.parser_type == ParserType.SINGLE_FILE:
        if not isinstance(path, (str, Path)):
            raise TypeError(f'Parser <{parser.__class__.__name__}> requires a single file')
        with open(path, parser.read_mode) as f:
            parser.deserialize(f.read())
    elif parser.parser_type == ParserType.EXTERNAL:
        parser.deserialize(path)
    elif parser.parser_type == ParserType.MULTI_FILE:
        if type(path) is str or isinstance(path, Path):
            files = expand(str(path), stride, offset)
        elif type(path) is list:
            files = [str(f) for f in path]
        else:
            raise TypeError(f'Parser <{parser.__class__.__name__}> requires a list of annotation files or an expandable file expression')

        # Default identify
        if identify is None:
            def identify(f): return os.path.splitext(os.path.basename(f))[0]

        for f in files:
            file_id = identify(f)
            with open(f, parser.read_mode) as f:
                parser.deserialize(f.read(), file_id)
    else:
        raise AttributeError(f'Parser <{parser.__class__.__name__}> has not defined a parser_type class attribute')

    df = parser.get_df()
    if parser.parser_type != ParserType.MULTI_FILE:
        if stride <= 0:
            raise ValueError('Stride must be a strictly positive integer')
        if offset < 0:
            raise ValueError('Offset must be a positive integer')

        if stride != 1 or offset != 0:
            df = util.select_images(df, df.image.cat.categories[offset::stride])

    return df


def save(df, fmt, path, **kwargs):
    """ Generate bounding box file(s) in any format.

    Args:
        df (pandas.DataFrame): Dataframe containing bounding boxes (annotations or detections)
        fmt (str or class or Parser): Format from the :ref:`brambox.io.formats <brambox.io.formats>` dictionary
        path (str): Path to the bounding box file/folder
        **kwargs (dict): Keyword arguments that are passed to the parser

    Warning:
        If the format is of the type :py:attr:`~brambox.io.parser.ParserType.SINGLE_FILE`,
        then the ``path`` parameter should contain a path to a **file**. |br|
        If the format is of the type :py:attr:`~brambox.io.parser.ParserType.MULTI_FILE`,
        then the ``path`` parameter should contain a path to a **folder**.
    """
    if isinstance(path, Path):
        path = str(path)

    # Create parser
    if type(fmt) is str:
        try:
            parser = formats[fmt](**kwargs)
        except KeyError as err:
            raise TypeError(f'Invalid parser {fmt}') from err
    elif isinstance(fmt, Parser):
        if len(kwargs) != 0:
            log.error(f'fmt argument is already an instantiated parser. Ignoring passed kwargs {kwargs}')
        parser = fmt
    elif issubclass(fmt, Parser):
        parser = fmt(**kwargs)
    else:
        raise TypeError(f'Invalid parser {fmt}')

    if parser.pre_serialize is not None:
        df = parser.pre_serialize(df.copy())

    # Write bounding boxes
    if parser.parser_type != ParserType.EXTERNAL:
        if parser.serialize_group is not None:
            data = df.groupby(parser.serialize_group).apply(parser.serialize)
        else:
            data = df.apply(parser.serialize, axis=1)

    if parser.parser_type == ParserType.SINGLE_FILE:
        if os.path.isdir(path):
            path = os.path.join(path, 'boxes' + parser.extension)
        elif len(os.path.splitext(path)[1]) == 0:
            path += parser.extension

        with open(path, parser.write_mode) as f:
            f.write(parser.header + data.str.cat(sep=parser.serialize_group_separator) + parser.footer)
    elif parser.parser_type == ParserType.EXTERNAL:
        parser.serialize(df, path)
    elif parser.parser_type == ParserType.MULTI_FILE:
        if not os.path.isdir(path):
            raise ValueError(f'Parser <{parser.__class__.__name__}> requires a path to a folder')

        for (file_id, rawdata) in data.iteritems():
            filename = os.path.join(path, file_id + parser.extension)
            directory = os.path.dirname(filename)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(filename, parser.write_mode) as f:
                f.write(parser.header + rawdata + parser.footer)
    else:
        raise AttributeError(f'Parser <{parser.__class__.__name__}> has not defined a parser_type class attribute')
