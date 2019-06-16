# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 10:06:08 2019

@author: Lee
"""

import yaml
import sys
import argparse

def locate_geometry(args):
    """ Pull file path and name from the input file (command line argument)"""
    input_file = args.inputfile #first element of args = input file
    with open(input_file, 'r') as f:
        # Pull the filename and path for geometry. return file path and name for future modification
        doc = yaml.load(f)
        path = doc['case']['geometry_file_directory'] # pulling path
        fname = doc['case']['geometry_file_name'] #pulling filename
        
        type_path = type(path) # object type of path
        type_fname = type(fname) # object type of fname
        
        if type_path == str:
            print("path is string")
        else:
            path = str(path) # conver to string type
            
        if type_fname == str:
            print("fname is string")
        else:
            fname = str(fname) # conver to string type
        
        # if type(path) == str:
            # concatenate the string
        file_path = path + '\\' + fname
        print(file_path)
        #else:
        return file_path
    
input_file1 = "C:\Oregon_State\Spring_2019\Soft_dev_eng\StoveOpt\tests\input_test_1.yaml" # Args formats for testing
input_file2 = "C:\Oregon_State\Spring_2019\Soft_dev_eng\StoveOpt\tests\input_test_2.yaml" # Args formats for testing
input_file3 = "C:\Oregon_State\Spring_2019\Soft_dev_eng\StoveOpt\tests\input_test_3.yaml" # Args formats for testing
input_file4 = "C:\Oregon_State\Spring_2019\Soft_dev_eng\StoveOpt\tests\input_test_4.yaml" # Args formats for testing
input_file5 = "C:\Oregon_State\Spring_2019\Soft_dev_eng\StoveOpt\tests\input_test_5.yaml" # Args formats for testing

""" Need to have the arguments directly fed into the parser..."""

"""# Construct the argument parse and parse the arguments
parser = argparse.ArgumentParser(description='Stove Optimization')
# File directory argument
parser.add_argument('-i', '--inputfile', required=True, help='path and filename for input.yaml')
args = parser.parse_args(sys.argv[1:])
"""

# Status: passing current test
expected_filename = "C:/Oregon_State/Spring_2019/Soft_dev_eng/StoveOpt/tests/Stove_test_Geometry.xlsx" # Known filename
def test_locate_geometry_1():
    """ output the file location of stove geometry as a string"""
    parser = argparse.ArgumentParser(description='Stove Optimization')
    parser.add_argument(input_file1) # Varying the input file
    args = parser.parse_args(sys.argv[1:])
    file_path = locate_geometry(args)
    assert file_path == expected_filename

def test_locate_geometry_2():
    """ output the file location of stove geometry as a string"""
    parser = argparse.ArgumentParser(description='Stove Optimization')
    parser.add_argument(input_file2) # Varying the input file
    args = parser.parse_args(sys.argv[1:])
    file_path = locate_geometry(args)
    file_path = locate_geometry(args)
    assert file_path == expected_filename
    
def test_locate_geometry_3():
    """ output the file location of stove geometry as a string"""
    parser = argparse.ArgumentParser(description='Stove Optimization')
    parser.add_argument(input_file3) # Varying the input file
    args = parser.parse_args(sys.argv[1:])
    file_path = locate_geometry(args)
    file_path = locate_geometry(args)
    assert file_path == expected_filename
    
def test_locate_geometry_4():
    """ output the file location of stove geometry as a string"""
    parser.add_argument(input_file4) # Varying the input file
    args = parser.parse_args(sys.argv[1:])
    file_path = locate_geometry(args)
    file_path = locate_geometry(args)
    assert file_path == expected_filename

def test_locate_geometry_5():
    """ output the file location of stove geometry as a string"""
    parser = argparse.ArgumentParser(description='Stove Optimization')
    parser.add_argument(input_file5) # Varying the input file
    args = parser.parse_args(sys.argv[1:])
    file_path = locate_geometry(args)
    file_path = locate_geometry(args)
    assert file_path == expected_filename
    
    