"""Autogenerate converter between some formats.

"""

import itertools
from rofetta.utils import output_as_tempfile
from . import routines
from rofetta.utils import format_from_filename, basename_from_filename


def converter(informat:str, outformat:str) -> callable:
    """Return a function that convert given informat to given outformat"""
    reader = getattr(routines, 'read_' + informat, None)
    writer = getattr(routines, 'write_' + outformat, None)
    if reader and writer:
        def make_converter(reader, writer):
            @output_as_tempfile
            def converter_func(fin:str, fout:str=None, *, reader=reader, writer=writer):
                with open(fin) as ifd, open(fout, 'w') as ofd:
                    for line in writer(reader(iter(ifd))):
                        ofd.write(line + '\n')
            return converter_func

        return make_converter(reader, writer)
    raise ValueError("No converter exist between {} and {}".format(informat, outformat))


def possible_conversions() -> [(str, str)]:
    "Yield pairs of possible converters, according to functions defined in routine"
    # get available readers and writers
    writers, readers = set(), set()
    for name, func in vars(routines).items():
        if callable(func):
            if name.startswith('read_'):
                readers.add(name[len('read_'):])
            if name.startswith('write_'):
                writers.add(name[len('write_'):])
    for reader, writer in itertools.product(readers, writers):
        if reader != writer:
            yield reader, writer

# make all possible converters
converters = {}  # (reader, writer): func
input_formats = set()
output_formats = set()
for reader, writer in possible_conversions():
    input_formats.add(reader)
    output_formats.add(writer)
    func = converter(reader, writer)
    converters[reader, writer] = func
    globals()[f'convert_{reader}_to_{writer}'] = func
    # print('MADE', reader, 'to', writer)


def convert(infile:str, outfile:str):
    "Call the converter to convert data in infile into outfile"
    reader = format_from_filename(infile)
    writer = format_from_filename(outfile)
    # print(reader, writer, tuple(converters.keys()))
    if (reader, writer) not in converters:
        raise ValueError(f"Does not have converter to go from {reader} to {writer}.")
    return converters[reader, writer](infile, outfile)
