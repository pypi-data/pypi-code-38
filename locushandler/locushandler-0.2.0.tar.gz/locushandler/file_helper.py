"""
Helper functions for Locus code parsing

"""
import numpy as np
from locushandler.params import ACT_GRAN_TO_FIELDS, RES_GRAN_TO_FIELDS


def gran_to_fields(str_gran, type_loci, dr, io):
    """
    Returns a list of the fields given a granularity and a type of field

    :param str_gran: (string) granularity with the format '4x6', '12x6x4x3', etc...
    :param type: (string) 'work' or 'resource'
    :param dr: (bool) True if you want to include the dr
    :param io: (bool) True if you want to include the io
    :return: (list of string) list of all corresponding Loci fields
    """
    try:
        if str_gran == 'full':
            str_gran = '36x6x4x3'
        actx = str_gran.find('x')
        fields_act = ACT_GRAN_TO_FIELDS[str_gran[:actx]]
        fields_res = RES_GRAN_TO_FIELDS[str_gran[actx + 1:]]
        
        fields_obj = ['obj_' + field for field in fields_res]
        # For a work Loci : [dr] + [act] + [obj] + [io]
        if type_loci == 'work':
            if dr:
                fields_dr = ['dr_' + field for field in fields_res]
                all_f = fields_dr + fields_act + fields_obj
            else:
                all_f = fields_act + fields_obj
            if io:
                fields_io = ['io_' + field for field in fields_res]
                all_f += fields_io
        # For a resource Loci : [sub] + [act] + [obj]
        else:
            all_f = ['subj_' + field for field in fields_res]
            all_f = all_f + fields_act + fields_obj

        return all_f
    except KeyError:
        print('Make sure the granularity specified has the following format:')
        print(
            '{act}x{res} with act in [1,4,12,36] and res in [1, 6, 6x4, 6x4x3] ')


