import pytest
import time
from unittest.mock import patch, call
import os
import subprocess
from .useful_functions import *

def test_is_number():
    Good_x = 1111
    Poor_x = "Not a number"
    Good_VarName = "VarName"
    Poor_VarName = 1111

    Poor_default = "Not a number"
    Poor_notes = 1111

    ### test is_number with Good inputs and no **kwargs ###
    try:
        is_number(Good_x,Good_VarName)
        Success = True
    except AssertionError:
        Success = False

    assert Success==True, is_number.__name__() + " failed with good inputs and default kwargs."

    ### test if x is a number ###
    try:
        is_number(Poor_x,Good_VarName)
        ErrorCaught = False
    except AssertionError:
        ErrorCaught = True

    assert ErrorCaught==True, is_number.__name__() + " failed when testing if x was a number."

    ### test if VarName is a str ###
    try:
        is_number(Good_x,Poor_VarName)
        ErrorCaught = False
    except AssertionError:
        ErrorCaught = True

    assert ErrorCaught==True, is_number.__name__() + " failed when testing if VarName is a str."

    ### test if default is a number ###
    try:
        is_number(Good_x,Good_VarName,default=Poor_default)
        ErrorCaught = False
    except AssertionError:
        ErrorCaught = True

    assert ErrorCaught==True, is_number.__name__() + " failed when testing if default (kwargs) is a number."

    ### test if notes is a str ###
    try:
        is_number(Good_x,Good_VarName,notes=Poor_notes)
        ErrorCaught = False
    except AssertionError:
        ErrorCaught = True

    assert ErrorCaught==True, is_number.__name__() + " failed when testing if notes (kwargs) is a str."

def test_save_figures():
    Good_Destination = "Good_Destination/"
    Poor_Destination_1 = 1111
    Poor_Destination_2 = "Not a good Destination"

    Good_SubFolder = "Good_SubFolder/"
    Poor_SubFolder_1 = 1111
    Poor_SubFolder_2 = "Not a good SubFolder"

    Good_BaseFileName = "Good_BaseFileName"
    Poor_BaseFileName = 1111

    Good_params = {"Good Params" : True}
    Poor_params = 1111

    Good_SaveAsPDF = True
    Poor_SaveAsPDF = "Not a good SaveAsPDF"

    ### test if Destination is a str ###
    try:
        save_figures(
            Poor_Destination_1,
            Good_BaseFileName,
            Good_params
        )
        ErrorCaught = False
    except AssertionError:
        ErrorCaught = True
    except TypeError:
        ErrorCaught = True

    assert ErrorCaught==True, save_figures.__name__() + " failed when testing if Destination is a str."

    ### test if Destination ends in '/' ###
    try:
        save_figures(
            Poor_Destination_2,
            Good_BaseFileName,
            Good_params
        )
        ErrorCaught = False
    except AssertionError:
        ErrorCaught = True

    assert ErrorCaught==True, save_figures.__name__() + " failed when testing if Destination ends in '/'."

    ### test if SubFolder is a str ###
    try:
        save_figures(
            Good_Destination,
            Good_BaseFileName,
            Good_params,
            SubFolder = Poor_SubFolder_1
        )
        ErrorCaught = False
    except AssertionError:
        ErrorCaught = True
    except TypeError:
        ErrorCaught = True

    assert ErrorCaught==True, save_figures.__name__() + " failed when testing if SubFolder is a str."

    ### test if SubFolder ends in '/' ###
    try:
        save_figures(
            Good_Destination,
            Good_BaseFileName,
            Good_params,
            SubFolder = Poor_SubFolder_2
        )
        ErrorCaught = False
    except AssertionError:
        ErrorCaught = True

    assert ErrorCaught==True, save_figures.__name__() + " failed when testing if SubFolder ends in '/'."

    ### test if params is a dict ###
    try:
        save_figures(
            Good_Destination,
            Good_BaseFileName,
            Poor_params,
        )
        ErrorCaught = False
    except AttributeError:
        ErrorCaught = True

    assert ErrorCaught==True, save_figures.__name__() + " failed when testing if params is a dict."

    ### test if SaveAsPDF is a bool ###
    try:
        save_figures(
            Good_Destination,
            Good_BaseFileName,
            Good_params,
            SaveAsPDF = Poor_SaveAsPDF
        )
        ErrorCaught = False
    except AssertionError:
        ErrorCaught = True

    assert ErrorCaught==True, save_figures.__name__() + " failed when testing if SaveAsPDF is a bool."
