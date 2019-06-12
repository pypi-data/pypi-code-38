# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 15:39:27 2019

@author: Lee
"""
import numpy

"""Need to figure out the correct_arguments script"""
def correct_arguments(args):
    """
    Goal is to convert the geometry file argument to working syntax: Single quote, back slash
    
    Args:
        
        args (dictionary): Object contains the contents of the input file specified by the user
    
    
    """
    input_file = args.inputfile
    with open(input_file, 'r') as f:
        doc = yaml.load(f)
        path = doc['case']['geometry_file_directory'] # pulling path
        fname = doc['case']['geometry_file_name'] #pulling filename
        # Figure out type for each input
        path_type = type(path)
        fname_type = type(fname)
        print(path_type)
        print(fname_type)
        if path_type == str:
            print('The path type is a string--now going to filter out quotes to yield singles')
            path_first_character = path[0]
            print(path_first_character)
        else:
            # Convert the path to string if needed
            path = str(path) 
        
        if fname_type == str:
            print('file name is a string')
            fname_first_character = fname[0]
            print(fname_first_character)
        else:
            # Convert fname to a string
            fname = str(fname)
        print('This is the fname')
        print(fname)
        print('This is the path')
        print(path)
        
import yaml
def locate_geometry(args):
    """
    Pull file path and name from the input file (command line argument)
    
    Args:
        
        args (dictionary): Object contains the contents of the input file specified by the user
    
    Returns:
        file_path (str): full file path for input stove geometry defined by user in input yaml file.
    
    
    """
    input_file = args.inputfile #first element of args = input file
    with open(input_file, 'r') as f:
        # Pull the filename and path for geometry. return file path and name for future modification
        doc = yaml.load(f)
        path = doc['case']['geometry_file_directory'] # pulling path
        fname = doc['case']['geometry_file_name'] #pulling filename
        # if type(path) == str:
            # concatenate the string
        file_path = path + '\\' + fname
        print(file_path)
        #else:
        return file_path
       
import xlrd
def extract_geometry(file_path):
    """
    Pulling Data from excel workbook
    
    Args:
    
        file_path (str): full file path for input stove geometry defined by user in input yaml file.
    
    Returns:
        pt#i (float): A series of points pulled from the user defined geometry
    
    """
    workbook = xlrd.open_workbook(file_path)
    worksheet = workbook.sheet_by_name('Outputs')
    pt0x = worksheet.cell(1,2).value
    pt0z = worksheet.cell(1,3).value
    pt0y = worksheet.cell(1,4).value
    pt1x = worksheet.cell(2,2).value
    pt1z = worksheet.cell(2,3).value
    pt1y = worksheet.cell(2,4).value
    pt2x = worksheet.cell(3,2).value
    pt2z = worksheet.cell(3,3).value
    pt2y = worksheet.cell(3,4).value
    pt3x = worksheet.cell(4,2).value
    pt3z = worksheet.cell(4,3).value
    pt3y = worksheet.cell(4,4).value
    pt4x = worksheet.cell(5,2).value
    pt4z = worksheet.cell(5,3).value
    pt4y = worksheet.cell(5,4).value
    pt5x = worksheet.cell(6,2).value
    pt5z = worksheet.cell(6,3).value
    pt5y = worksheet.cell(6,4).value
    pt6x = worksheet.cell(7,2).value
    pt6z = worksheet.cell(7,3).value
    pt6y = worksheet.cell(7,4).value
    pt7x = worksheet.cell(8,2).value
    pt7z = worksheet.cell(8,3).value
    pt7y = worksheet.cell(8,4).value
    pt8x = worksheet.cell(9,2).value
    pt8z = worksheet.cell(9,3).value
    pt8y = worksheet.cell(9,4).value
    pt9x = worksheet.cell(10,2).value
    pt9z = worksheet.cell(10,3).value
    pt9y = worksheet.cell(10,4).value
    pt10x = worksheet.cell(11,2).value
    pt10z = worksheet.cell(11,3).value
    pt10y = worksheet.cell(11,4).value
    pt11x = worksheet.cell(12,2).value
    pt11z = worksheet.cell(12,3).value
    pt11y = worksheet.cell(12,4).value
    pt12x = worksheet.cell(13,2).value
    pt12z = worksheet.cell(13,3).value
    pt12y = worksheet.cell(13,4).value
    pt13x = worksheet.cell(14,2).value
    pt13z = worksheet.cell(14,3).value
    pt13y = worksheet.cell(14,4).value
    pt14x = worksheet.cell(15,2).value
    pt14z = worksheet.cell(15,3).value
    pt14y = worksheet.cell(15,4).value
    pt15x = worksheet.cell(16,2).value
    pt15z = worksheet.cell(16,3).value
    pt15y = worksheet.cell(16,4).value
    U_100x = worksheet.cell(17,2).value
    U_100z = worksheet.cell(17,3).value # Not really using the other 2-dimensions for now
    U_100y = worksheet.cell(17,4).value
    if pt15z == 0:
        print("Top point has a 0 height value--error in data import")
    return U_100x, U_100y, U_100z, pt1x, pt1z, pt1y, pt2x, pt2z, pt2y, pt3x, pt3z, pt3y, pt4x, pt4z, pt4y, pt5x, pt5z, pt5y, pt6x, pt6z, pt6y, pt7x, pt7z, pt7y, pt8x, pt8z, pt8y, pt9x, pt9z, pt9y, pt10x, pt10z, pt10y, pt11x, pt11z, pt11y, pt12x, pt12z, pt12y, pt13x, pt13z, pt13y,  pt14x, pt14z, pt14y, pt15x, pt15z, pt15y, pt0x, pt0z, pt0y

# Create additional front face points including wood zone
def create_fuel_blocks(pt0x, pt1x):
    """
    Creates geometry for the fuel block with the following assumptions:  Rectangular fuel source, Centered along the vertical axis of the combustion chamber, Width of fuel block is half the diameter of the combustion chamber, Assumed fuel height of 3 inches (0.0762 m), bottom of the fuel is 3 inches off the ground.
    
    Args:
    
        pt0x (float): origin x-coordinate of cookstove geometry        
        pt1x (float): Bottom east vertice of cookstove combustion chamber
    
     Returns:
         
         points (float): x,y,z coordinates of the wood fuel block
    
    """
    fuel_width = 0.5*(pt1x - pt0x)
    fuel_x_center = fuel_width
    fuel_x_left_coord = fuel_x_center - (fuel_width)/2
    fuel_x_right_coord = fuel_x_center + (fuel_width)/2
    fuel_height = 0.02 # [m]
    fuel_bottom_coords = 0.02
    fuel_top_coords = fuel_bottom_coords + fuel_height
    pt16x = fuel_x_left_coord
    pt17x = fuel_x_right_coord
    pt18x = fuel_x_right_coord
    pt19x = fuel_x_left_coord
    pt16z = fuel_bottom_coords
    pt17z = fuel_bottom_coords
    pt18z = fuel_top_coords
    pt19z = fuel_top_coords
    pt16y = 0
    pt17y = 0
    pt18y = 0
    pt19y = 0
    return pt17x, pt18x, pt19x, pt16x, pt17z, pt18z, pt19z, pt16z, pt17y, pt18y, pt19y, pt16y

# 20 defined by 6x and 14z
# 21 defined by 7x and 15z
# 44 defined by 14x and 9z
# 46 defined by 15x and 8z    
def create_additional_front_points(pt6x, pt7x, pt14x, pt9z, pt15x, pt8z, pt14z, pt9x, pt8x, pt15z):
    """
    Create pot surface points to create faces--Naming them 21(L)-22(R) to not collide with current fuel vert numbers
    
    Args:
        points (float): cookstove geometry
    
    Returns:
        
        points (float): series of points created as the back plane of the stove. Used to create a 2D geometry
    
    
    """
    # Left point
    pt20x = pt6x
    pt20z = pt14z
    pt20y = 0
    # Right point
    pt21x = pt7x
    pt21z = pt15z
    pt21y = 0
    
    pt44x = pt14x
    pt44z = pt9z
    pt44y = 0
    
    pt46x = pt15x
    pt46z = pt8z
    pt46y = 0
    
    pt48x = pt9x
    pt48z = pt14z
    pt48y = 0
    
    pt50x =  pt8x
    pt50z = pt15z
    pt50y = 0
    
    
    return pt48x, pt48z, pt48y, pt20x, pt20z, pt20y, pt21x, pt21z, pt21y, pt44x, pt44z, pt44y, pt46x, pt46z, pt46y, pt50x, pt50z, pt50y

# Stove front (0-15), wood front (16-19), additional points front (20,21,44,46)
def points_to_strings(pt1x, pt1z, pt1y, pt2x, pt2z, pt2y, pt3x, pt3z, pt3y, pt4x, pt4z, pt4y, pt5x, pt5z, pt5y, pt6x, pt6z, pt6y, pt7x, pt7z, pt7y, pt8x, pt8z, pt8y, pt9x, pt9z, pt9y, pt10x, pt10z, pt10y, pt11x, pt11z, pt11y, pt12x, pt12z, pt12y, pt13x, pt13z, pt13y,  pt14x, pt14z, pt14y, pt15x, pt15z, pt15y, pt0x, pt0z, pt0y, pt17x, pt18x, pt19x, pt16x, pt17z, pt18z, pt19z, pt16z, pt17y, pt18y, pt19y, pt16y, pt20x, pt20z, pt20y, pt21x, pt21z, pt21y, pt44x, pt44z, pt44y, pt46x, pt46z, pt46y, pt48x, pt48y, pt48z, pt50x, pt50y, pt50z):
    """
    Take in the raw vertice information from spreadsheet, and format the floats into strings->For front vertices
    
    Args:
        points (float): all front coordinates
    
    Returns:
        points as strings (str): Coordinates converted to strings compatible with openfoam convention (length 5).
    

    """
    pt0xstr= str(pt0x)[:5]
    pt0zstr = str(pt0z)[:5]
    pt0ystr = str(pt0y)[:5]  
    pt1xstr= str(pt1x)[:5]
    pt1zstr = str(pt1z)[:5]
    pt1ystr = str(pt1y)[:5]
    pt2xstr= str(pt2x)[:5]
    pt2zstr = str(pt2z)[:5]
    pt2ystr = str(pt2y)[:5]
    pt3xstr= str(pt3x)[:5]
    pt3zstr = str(pt3z)[:5]
    pt3ystr = str(pt3y)[:5]
    pt4xstr= str(pt4x)[:5]
    pt4zstr = str(pt4z)[:5]
    pt4ystr = str(pt4y)[:5]
    pt5xstr= str(pt5x)[:5]
    pt5zstr = str(pt5z)[:5]
    pt5ystr = str(pt5y)[:5]
    pt6xstr= str(pt6x)[:5]
    pt6zstr = str(pt6z)[:5]
    pt6ystr = str(pt6y)[:5]
    pt7xstr= str(pt7x)[:5]
    pt7zstr = str(pt7z)[:5]
    pt7ystr = str(pt7y)[:5]
    pt8xstr= str(pt8x)[:5]
    pt8zstr = str(pt8z)[:5]
    pt8ystr = str(pt8y)[:5]
    pt9xstr= str(pt9x)[:5]
    pt9zstr = str(pt9z)[:5]
    pt9ystr = str(pt9y)[:5]
    pt10xstr= str(pt10x)[:5]
    pt10zstr = str(pt10z)[:5]
    pt10ystr = str(pt10y)[:5]
    pt11xstr= str(pt11x)[:5]
    pt11zstr = str(pt11z)[:5]
    pt11ystr = str(pt11y)[:5]
    pt12xstr= str(pt12x)[:5]
    pt12zstr = str(pt12z)[:5]
    pt12ystr = str(pt12y)[:5]
    pt13xstr= str(pt13x)[:5]
    pt13zstr = str(pt13z)[:5]
    pt13ystr = str(pt13y)[:5]
    pt14xstr= str(pt14x)[:5]
    pt14zstr = str(pt14z)[:5]
    pt14ystr = str(pt14y)[:5]
    pt15xstr= str(pt15x)[:5]
    pt15zstr = str(pt15z)[:5]
    pt15ystr = str(pt15y)[:5]
    
    pt16xstr= str(pt16x)[:5]
    pt16zstr = str(pt16z)[:5]
    pt16ystr = str(pt16y)[:5]
    pt17xstr= str(pt17x)[:5]
    pt17zstr = str(pt17z)[:5]
    pt17ystr = str(pt17y)[:5]
    pt18xstr= str(pt18x)[:5]
    pt18zstr = str(pt18z)[:5]
    pt18ystr = str(pt18y)[:5]
    pt19xstr= str(pt19x)[:5]
    pt19zstr = str(pt19z)[:5]
    pt19ystr = str(pt19y)[:5]
    
    pt20xstr= str(pt20x)[:5]
    pt20zstr = str(pt20z)[:5]
    pt20ystr = str(pt20y)[:5]
    pt21xstr= str(pt21x)[:5]
    pt21zstr = str(pt21z)[:5]
    pt21ystr = str(pt21y)[:5]
    pt44xstr= str(pt44x)[:5]
    pt44zstr = str(pt44z)[:5]
    pt44ystr = str(pt44y)[:5]
    pt46xstr= str(pt46x)[:5]
    pt46zstr = str(pt46z)[:5]
    pt46ystr = str(pt46y)[:5]
    
    pt48xstr= str(pt48x)[:5]
    pt48zstr = str(pt48z)[:5]
    pt48ystr = str(pt48y)[:5]
    
    pt50xstr= str(pt50x)[:5]
    pt50zstr = str(pt50z)[:5]
    pt50ystr = str(pt50y)[:5]
    return pt1xstr, pt1zstr, pt1ystr, pt2xstr, pt2zstr, pt2ystr, pt3xstr, pt3zstr, pt3ystr, pt4xstr, pt4zstr, pt4ystr, pt5xstr, pt5zstr, pt5ystr, pt6xstr, pt6zstr, pt6ystr, pt7xstr, pt7zstr, pt7ystr, pt8xstr, pt8zstr, pt8ystr, pt9xstr, pt9zstr, pt9ystr, pt10xstr, pt10zstr, pt10ystr, pt11xstr, pt11zstr, pt11ystr, pt12xstr, pt12zstr, pt12ystr, pt13xstr, pt13zstr, pt13ystr,  pt14xstr, pt14zstr, pt14ystr, pt15xstr, pt15zstr, pt15ystr, pt0xstr, pt0zstr, pt0ystr, pt16xstr, pt16zstr, pt16ystr, pt17xstr, pt17zstr, pt17ystr, pt18xstr, pt18zstr, pt18ystr, pt19xstr, pt19zstr, pt19ystr, pt20xstr, pt20zstr, pt20ystr, pt21xstr, pt21zstr, pt21ystr, pt44xstr, pt44zstr, pt44ystr, pt46xstr, pt46zstr, pt46ystr, pt48xstr, pt48zstr, pt48ystr, pt50xstr, pt50zstr, pt50ystr


# Stove front (0-15), wood front (16-19), additional points front (20,21,44,46)
# x = x1, y = x2, z = x3 coordinates based on OpenFOAM convention
def vertice_concatenate(pt1xstr, pt1zstr, pt1ystr, pt2xstr, pt2zstr, pt2ystr, pt3xstr, pt3zstr, pt3ystr, pt4xstr, pt4zstr, pt4ystr, pt5xstr, pt5zstr, pt5ystr, pt6xstr, pt6zstr, pt6ystr, pt7xstr, pt7zstr, pt7ystr, pt8xstr, pt8zstr, pt8ystr, pt9xstr, pt9zstr, pt9ystr, pt10xstr, pt10zstr, pt10ystr, pt11xstr, pt11zstr, pt11ystr, pt12xstr, pt12zstr, pt12ystr, pt13xstr, pt13zstr, pt13ystr,  pt14xstr, pt14zstr, pt14ystr, pt15xstr, pt15zstr, pt15ystr, pt0xstr, pt0zstr, pt0ystr, pt16xstr, pt16zstr, pt16ystr, pt17xstr, pt17zstr, pt17ystr, pt18xstr, pt18zstr, pt18ystr, pt19xstr, pt19zstr, pt19ystr, pt20xstr, pt20zstr, pt20ystr, pt21xstr, pt21zstr, pt21ystr, pt44xstr, pt44zstr, pt44ystr, pt46xstr, pt46zstr, pt46ystr, pt48xstr, pt48zstr, pt48ystr, pt50xstr, pt50zstr, pt50ystr): 
    """
    Convert the individual vertex strings and concatenate to the format required for blockmeshdict file
    
    Args:
        points as strings (str): Coordinates converted to strings compatible with openfoam convention (length 5).
    
    Returns:
        concatenated front points (str): The x,y,z values of front points concatenated into single vertice location
    
    
    """
    # Stove Body
    pt0str = "(" + pt0ystr + " " + pt0xstr + " " + pt0zstr + ")"
    pt1str = "(" + pt1ystr + " " + pt1xstr + " " + pt1zstr + ")"
    pt2str = "(" + pt2ystr + " " + pt2xstr + " " + pt2zstr + ")"
    pt3str = "(" + pt3ystr + " " + pt3xstr + " " + pt3zstr + ")"
    pt4str = "(" + pt4ystr + " " + pt4xstr + " " + pt4zstr + ")"
    pt5str = "(" + pt5ystr + " " + pt5xstr + " " + pt5zstr + ")"
    pt6str = "(" + pt6ystr + " " + pt6xstr + " " + pt6zstr + ")"
    pt7str = "(" + pt7ystr + " " + pt7xstr + " " + pt7zstr + ")"
    pt8str = "(" + pt8ystr + " " + pt8xstr + " " + pt8zstr + ")"
    pt9str = "(" + pt9ystr + " " + pt9xstr + " " + pt9zstr + ")"
    pt10str = "(" + pt10ystr + " " + pt10xstr + " " + pt10zstr + ")"
    pt11str = "(" + pt11ystr + " " + pt11xstr + " " + pt11zstr + ")"
    pt12str = "(" + pt12ystr + " " + pt12xstr + " " + pt12zstr + ")"
    pt13str = "(" + pt13ystr + " " + pt13xstr + " " + pt13zstr + ")"
    pt14str = "(" + pt14ystr + " " + pt14xstr + " " + pt14zstr + ")"
    pt15str = "(" + pt15ystr + " " + pt15xstr + " " + pt15zstr + ")"
    
    # Wood
    pt16str = "(" + pt16ystr + " " + pt16xstr + " " + pt16zstr + ")"
    pt17str = "(" + pt17ystr + " " + pt17xstr + " " + pt17zstr + ")"
    pt18str = "(" + pt18ystr + " " + pt18xstr + " " + pt18zstr + ")"
    pt19str = "(" + pt19ystr + " " + pt19xstr + " " + pt19zstr + ")"    
    
    # Additional front pts
    pt20str = "(" + pt20ystr + " " + pt20xstr + " " + pt20zstr + ")"
    pt21str = "(" + pt21ystr + " " + pt21xstr + " " + pt21zstr + ")"
    pt44str = "(" + pt44ystr + " " + pt44xstr + " " + pt44zstr + ")"
    pt46str = "(" + pt46ystr + " " + pt46xstr + " " + pt46zstr + ")"
    pt48str = "(" + pt48ystr + " " + pt48xstr + " " + pt48zstr + ")"
    pt50str = "(" + pt50ystr + " " + pt50xstr + " " + pt50zstr + ")"
    
    
    return pt0str, pt1str, pt2str, pt3str, pt4str, pt5str, pt6str, pt7str, pt8str, pt9str, pt10str, pt11str, pt12str, pt13str, pt14str, pt15str, pt16str, pt17str, pt18str, pt19str, pt20str, pt21str, pt44str, pt46str, pt48str, pt50str


def create_back_points(shift, pt1xstr, pt1zstr, pt1ystr, pt2xstr, pt2zstr, pt2ystr, pt3xstr, pt3zstr, pt3ystr, pt4xstr, pt4zstr, pt4ystr, pt5xstr, pt5zstr, pt5ystr, pt6xstr, pt6zstr, pt6ystr, pt7xstr, pt7zstr, pt7ystr, pt8xstr, pt8zstr, pt8ystr, pt9xstr, pt9zstr, pt9ystr, pt10xstr, pt10zstr, pt10ystr, pt11xstr, pt11zstr, pt11ystr, pt12xstr, pt12zstr, pt12ystr, pt13xstr, pt13zstr, pt13ystr,  pt14xstr, pt14zstr, pt14ystr, pt15xstr, pt15zstr, pt15ystr, pt0xstr, pt0zstr, pt0ystr, pt16xstr, pt16zstr, pt16ystr, pt17xstr, pt17zstr, pt17ystr, pt18xstr, pt18zstr, pt18ystr, pt19xstr, pt19zstr, pt19ystr, pt20xstr, pt20zstr, pt20ystr, pt21xstr, pt21zstr, pt21ystr, pt44xstr, pt44zstr, pt44ystr, pt46xstr, pt46zstr, pt46ystr, pt48xstr, pt48zstr, pt48ystr, pt50xstr, pt50ystr, pt50zstr):
    """
    Back coordinates of the cookstove--simply shifting the x2 (y) coordinate back by a value shift
    
    Args:
        concatenated back points (str): The x,y,z values of back points concatenated into single vertice location
    
    
    """
    if shift > 0:
        shift = shift*(-1)
        print('Shift multiplied by -1')
    elif shift == 0:
        print('Shift is equal to zero: get ready for some errors')
    elif shift < 0:
        print('Shift is less than zero naturally')
    shift_str = str(shift)[:5] # converting to string
    
    # Stove Body--back 
    pt22str = "(" + shift_str + " " + pt0xstr + " " + pt0zstr + ")"
    pt23str = "(" + shift_str + " " + pt1xstr + " " + pt1zstr + ")"
    pt24str = "(" + shift_str + " " + pt2xstr + " " + pt2zstr + ")"
    pt25str = "(" + shift_str + " " + pt3xstr + " " + pt3zstr + ")"
    pt26str = "(" + shift_str + " " + pt4xstr + " " + pt4zstr + ")"
    pt27str = "(" + shift_str + " " + pt5xstr + " " + pt5zstr + ")"
    pt28str = "(" + shift_str + " " + pt6xstr + " " + pt6zstr + ")"
    pt29str = "(" + shift_str + " " + pt7xstr + " " + pt7zstr + ")"
    pt30str = "(" + shift_str + " " + pt8xstr + " " + pt8zstr + ")"
    pt31str = "(" + shift_str + " " + pt9xstr + " " + pt9zstr + ")"
    pt32str = "(" + shift_str + " " + pt10xstr + " " + pt10zstr + ")"
    pt33str = "(" + shift_str + " " + pt11xstr + " " + pt11zstr + ")"
    pt34str = "(" + shift_str + " " + pt12xstr + " " + pt12zstr + ")"
    pt35str = "(" + shift_str + " " + pt13xstr + " " + pt13zstr + ")"
    pt36str = "(" + shift_str + " " + pt14xstr + " " + pt14zstr + ")"
    pt37str = "(" + shift_str + " " + pt15xstr + " " + pt15zstr + ")"
    
    # Wood
    pt38str = "(" + shift_str + " " + pt16xstr + " " + pt16zstr + ")"
    pt39str = "(" + shift_str + " " + pt17xstr + " " + pt17zstr + ")"
    pt40str = "(" + shift_str + " " + pt18xstr + " " + pt18zstr + ")"
    pt41str = "(" + shift_str + " " + pt19xstr + " " + pt19zstr + ")"    
    
    # Additional front pts
    pt42str = "(" + shift_str + " " + pt20xstr + " " + pt20zstr + ")"
    pt43str = "(" + shift_str + " " + pt21xstr + " " + pt21zstr + ")"
    pt45str = "(" + shift_str + " " + pt44xstr + " " + pt44zstr + ")"
    pt47str = "(" + shift_str + " " + pt46xstr + " " + pt46zstr + ")"
    pt49str = "(" + shift_str + " " + pt48xstr + " " + pt48zstr + ")"
    pt51str = "(" + shift_str + " " + pt50xstr + " " + pt50zstr + ")"
    
    
    return pt22str, pt23str, pt24str, pt25str, pt26str, pt27str, pt28str, pt29str, pt30str, pt31str, pt32str, pt33str, pt34str, pt35str, pt36str, pt37str, pt38str, pt39str, pt40str, pt41str, pt42str, pt43str, pt45str, pt47str, pt49str, pt51str
    
    
    
