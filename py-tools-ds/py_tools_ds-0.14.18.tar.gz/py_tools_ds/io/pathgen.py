# -*- coding: utf-8 -*-

import tempfile
import os

__author__ = "Daniel Scheffler"


def get_tempfile(ext=None, prefix=None, tgt_dir=None):
    """Returns the path to a tempfile.mkstemp() file that can be passed to any function that expects a physical path.
    The tempfile has to be deleted manually.
    :param ext:     file extension (None if None)
    :param prefix:  optional file prefix
    :param tgt_dir: target directory (automatically set if None)
     """
    prefix = 'py_tools_ds__' if prefix is None else prefix
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=ext, dir=tgt_dir)
    os.close(fd)
    return path


def get_generic_outpath(dir_out='', fName_out='', prefix='', ext='', create_outDir=True,
                        prevent_overwriting=False):
    """Generates an output path accourding to the given parameters.

    :param dir_out:             output directory
    :param fName_out:           output filename
    :param prefix:              a prefix for the output filename. ignored if fName_out is given
    :param ext:                 the file extension to use
    :param create_outDir:       whether to automatically create the output directory or not
    :param prevent_overwriting: whether to prevent that a output filename is chosen that already exist in the filesystem
    :return:
    """
    dir_out = dir_out if dir_out else os.path.abspath(os.path.curdir)
    if create_outDir and not os.path.isdir(dir_out):
        os.makedirs(dir_out)

    if not fName_out:
        fName_out = '%soutput' % prefix + ('.%s' % ext if ext else '')
        if prevent_overwriting:
            count = 1
            while os.path.exists(os.path.join(dir_out, fName_out)):
                if count == 1:
                    fName_out += str(count)
                else:
                    fName_out[-1] = str(count)

    return os.path.join(dir_out, fName_out)
