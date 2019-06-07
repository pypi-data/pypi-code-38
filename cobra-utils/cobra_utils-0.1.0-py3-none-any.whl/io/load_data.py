# -*- coding: utf-8 -*-

from __future__ import absolute_import

import cobra


def load_model(filename, format ='matlab'):
    '''
    This function opens a metabolic reconstruction from a given format.

    Parameters
    ----------
    filename : str
        Filename of the model to open. It is preferable to use absolute path.

    format : str, 'matlab' by default.
        Format of the file containing the model. Options to use:
        'json' for .json file
        'matlab' for .mat file
        'sbml' for .xml file
        'yaml' for  .yaml or .yml file

    Returns
    -------
    model : cobra.core.Model.Model
        The resulting cobra model.
    '''
    print('Loading genome-scale model')
    try:
        if format == 'json':
            model = cobra.io.load_json_model(filename)
        elif format == 'matlab':
            model = cobra.io.load_matlab_model(filename)
        elif format == 'sbml':
            model = cobra.io.read_sbml_model(filename)
        elif format == 'yaml':
            model = cobra.io.load_yaml_model(filename)
        else:
            raise NotImplementedError("Format {} not implemented. Specify a correct format for the model".format(format))
    except:
        raise ImportError("The file has an incorrect format or does not match with implemented formats")
    print('Model correctly loaded.')
    return model