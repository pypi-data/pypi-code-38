# encoding: utf8
"""Routines converting various format into ASP.

"""
import os
import csv
import shutil
import tempfile
import itertools
from biseau import core


def format_from_filename(fname:str) -> str or None:
    """Return the format associated with given filename"""
    return os.path.splitext(fname)[1][1:]


def convert(fin:str, fout:str):
    """Convert content found in input file to the format inferred from
    given output filename, where it's then wrote.

    """
    input_format = format_from_filename(fin)
    output_format = format_from_filename(fout)

    if output_format != 'lp':
        raise NotImplementedError("Not in the scope of this project")

    if input_format == output_format:
        shutil.copy(fin, fout)
    elif input_format not in convert_to_lp:
        raise NotImplementedError("Format {} not handled".format(input_format))
    else:
        convert_to_lp[input_format](fin, fout)


def convert_cxt_to_lp(fin:str, fout:str):
    with open(fin) as ifd, open(fout, 'w') as ofd:
        assert next(ifd) == 'B\n', 'expects a B'
        assert next(ifd) == '\n', 'expects empty line'
        nb_obj, nb_att = map(int, (next(ifd), next(ifd)))
        assert next(ifd) == '\n', 'expects empty line'
        objects = tuple(next(ifd).strip() for _ in range(nb_obj))
        attributes = tuple(next(ifd).strip() for _ in range(nb_att))
        for object, properties in zip(objects, ifd):
            intent = itertools.compress(attributes, (char.lower() == 'x'
                                                     for char in properties))
            for prop in intent:
                ofd.write('rel("{}","{}").'.format(object, prop))


def convert_slf_to_lp(fin:str, fout:str):
    with tempfile.NamedTemporaryFile('w', delete=True) as fd:
        core.slf_to_cxt.file_to_file(fin, fd.name)
        return convert_cxt_to_lp(fd.name, fout)


def convert_txt_to_lp(fin:str, fout:str):
    with open(fin) as ifd, open(fout, 'w') as ofd:
        lines = csv.reader(ifd, delimiter='|')
        attributes = tuple(map(str.strip, next(lines)[1:-1]))  # first and last fields are empty
        for object, *props in lines:
            intent = itertools.compress(attributes, (char.strip().lower() == 'x'
                                                     for char in props))
            for prop in intent:
                ofd.write('rel("{}","{}").'.format(object.strip(), prop))


def convert_csv_to_lp(fin:str, fout:str):
    with open(fin) as ifd, open(fout, 'w') as ofd:
        lines = csv.reader(ifd, delimiter=',')
        attributes = tuple(map(str.strip, next(lines)[1:]))  # first field is empty
        for object, *props in lines:
            intent = itertools.compress(attributes, (char.strip().lower() == 'x'
                                                     for char in props))
            for prop in intent:
                ofd.write('rel("{}","{}").'.format(object.strip(), prop))


convert_to_lp = {
    'cxt': convert_cxt_to_lp,
    'slf': convert_slf_to_lp,
    'txt': convert_txt_to_lp,
    'csv': convert_csv_to_lp,
}
