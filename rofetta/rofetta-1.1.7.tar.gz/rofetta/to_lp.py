"""All functions allowing one to convert to lp"""

import csv
import itertools
from rofetta.utils import output_as_tempfile, as_asp_value


@output_as_tempfile
def convert_cxt_to_lp(fin:str, fout:str):
    """Convert input cxt data in lp format.

    fin -- readable file containing cxt data
    fout -- writable file

    """
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


@output_as_tempfile
def convert_txt_to_lp(fin:str, fout:str):
    with open(fin) as ifd, open(fout, 'w') as ofd:
        lines = csv.reader(ifd, delimiter='|')
        attributes = tuple(map(str.strip, next(lines)[1:-1]))  # first and last fields are empty
        for object, *props in lines:
            intent = itertools.compress(attributes, (char.strip().lower() == 'x'
                                                     for char in props))
            for prop in intent:
                ofd.write('rel("{}","{}").'.format(object.strip(), prop))


@output_as_tempfile
def convert_csv_to_lp(fin:str, fout:str):
    with open(fin) as ifd, open(fout, 'w') as ofd:
        lines = csv.reader(ifd, delimiter=',')
        attributes = tuple(map(str.strip, next(lines)[1:]))  # first field is empty
        for object, *props in lines:
            intent = itertools.compress(attributes, (char.strip().lower() == 'x'
                                                     for char in props))
            for prop in intent:
                ofd.write('rel("{}","{}").'.format(object.strip(), prop))


from_format = {
    'cxt': convert_cxt_to_lp,
    'txt': convert_txt_to_lp,
    'csv': convert_csv_to_lp,
}
