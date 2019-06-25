import contextlib
import numpy as np

import config

from functools import partial, reduce
import warnings

from errors import ModeError

import pyehub 
import operator

from pyehub.energy_hub.ehub_model import EHubModel

"""This file is a collection of functions to interact with PyEHub."""

#TODO: yaml loader & check if file exists
def get_xlsx(excel_file: str = config.files.get("xlsx")):
    return excel_file

def get_hub():
    """Generates the base PyEHub model from the excel file."""
    # could check the settings to see what type of ehub model to create
    data_file = get_xlsx()
    model = pyehub.energy_hub.EHubModel(excel=data_file)
    return model

def get_by_path(root, items):
    """Access a nested object in root by item sequence. Used to navigate PyEHub's not flat dict."""
    #TODO: inset try statement here incase the parameter doesn't exist to fail gracefuly
    return reduce(operator.getitem, items, root)

def set_by_path(root, items, value):
    """Set a value in a nested object in root by item sequence. Used to set values in PyEHub's not flat dict."""
    get_by_path(root, items[:-1])[items[-1]] = value
    
# no longer necessary due to restructure of EHProblem    
def name_getter(dict):
    """Get list of names from a dictionary. Used to get the objective names for EHProblem."""
    namelist = []
    for item in dict:
        name = ''
        for part in item:
            if(name == ''):
                name = name + part
            else:
                name = name + ':' + part  
        namelist.append(name)
    return namelist

def pyehub_parameter_editor(hub, parameters, values:list):
    """Changes the __dict__ of the energy hub for the parameters specified
    on initialization with the values given to evaluator."""
    if (len(parameters) > 0): # There are paremeters to edit
        for (parameter,value) in zip(parameters,values):
            # Change the value of the paremeter in the model's dict
            set_by_path(hub.__dict__,parameter,value)