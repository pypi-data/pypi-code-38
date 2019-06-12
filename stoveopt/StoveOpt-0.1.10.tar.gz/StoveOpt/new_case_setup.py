# -*- coding: utf-8 -*-
"""
Created on Thu May 23 11:06:19 2019

@author: Lee
"""

# Following the post processing efforts, create new case files for the next round of simulations
# Feed the new cases into the create block mesh, run surrounding cases, and post_processor for iteration
  
import numpy as np
import os
from shutil import copytree


def define_new_case_names(v_cases_total_vector):
    """
    Create new case_ folders in the foamfiles folder. Named based on velocities computed in post_processor
    
    Args:
        v_cases_total_vector (array): Numpy array listing four velocities to be added to the case queue
      
    Returns:
        
        case_name_list (dict): List of strings each corresponding to a new case file. Named based on velocity values converted to string.
        
        v_cases_total_vector_string (dict): Velocities converted to string dtype
        
        v_boundary_strings (dict): Velocty data converted to string compatible with boundary condition file

    
    """
    # Algorithm ==>
    # Pull in the new velocities vector
    # convert the vector to a string of length 6. 
    # delete the "." periods from the string vector
    
    # Empty np array with datatype string
    v_cases_total_vector_string = [] # empty list
    v_boundary_strings = [] # empty list for strings used in editing the boundary condition files
    
    y = 0 # Looping index
    while y < len(v_cases_total_vector):
        v_string = str(v_cases_total_vector[y])
        v_string_stripped = v_string.strip("[")
        v_string_stripped_velocity_strs = v_string_stripped.strip("]")
        v_string_stripped = v_string_stripped_velocity_strs.replace(".", "") # replace period with nothing
        print("velocity value as string stripped")
        print(v_string_stripped)
        # eliminate the first and last character of each string (the brackets)
        print("y value")
        print(y)
        # Add string to a list
        v_cases_total_vector_string.append(v_string_stripped)
        v_boundary_strings.append(v_string_stripped_velocity_strs)
        
        print("v vector string for case titles")
        print(v_cases_total_vector_string)
        
        print("velocity numbers for the boundary condition files")
        print(v_boundary_strings)
    
        #v_cases_total_vector_string[y] = v_string 
        #print("v cases total vector string")
        #print(v_cases_total_vector_string)
        y = y + 1
        
    # add "case_" to the front of each string
    prepend = "case_"
    
    case_name_list = []
    x = 0
    while x < len(v_cases_total_vector):
        # extract the non prepended string from the v_cases_total_vector_string
        vel_string = v_cases_total_vector_string[x]
        case_name = prepend + vel_string
        print("case name")
        print(case_name)
        case_name_list.append(case_name)
        x = x + 1
    print("case name list")
    print(case_name_list)
    return case_name_list, v_cases_total_vector_string, v_boundary_strings

def  create_case_directories(case_name_list):
    """Create the directories for next batch of simulations within the foamfiles dir
    
    Args:
    
        case_name_list (dict): List of strings each corresponding to a new case file. Named based on velocity values converted to string.
    
    
    Returns:
        
        full_case_paths (dict): List of full paths for new cases to be added. Compatible with windows os.
    

    """
    # Current working directory
    current_dir = os.getcwd()
    print("current working directory")
    
    # Directory steps for foamfiles
    directory_steps = "\\foamfiles\\counterFlowFlame2D\\"
    
    # Full root path
    full_root_path = current_dir + directory_steps
    
    print("full_path")
    print(full_root_path)
    
    # Empty full path vector
    full_case_paths = []
    x = 0
    while x < len(case_name_list):
        # add path root the case names based on index x, use mkdir command to make directories
        # if directories exist already do nothing and move to next x
        case_name = case_name_list[x]
        full_path_x = full_root_path + case_name
        print("iterative full path")
        print(full_path_x)
        
        # Append the full paths vector
        full_case_paths.append(full_path_x)
        
        # Check directory existence
        # Create new path if the directory doesn't exist, print and move on if it does
        exists = os.path.isdir(full_path_x)
        if exists == True:
            print("case folder ALREADY EXISTS")
        else:
            print("creating path: ")
            print(full_path_x)
            os.mkdir(full_path_x)
        x = x + 1
    return full_case_paths        

def add_templates(full_case_paths):
    """Add the template files to the new case directories
    
    Args:
        full_case_paths (dict): List of full paths for new cases to be added. Compatible with windows os.
 
    Returns:
        
        zero_file_paths (dict): List of paths leading to initial condition files for each newly added case
    
        constant_file_paths (dict): List of paths leading to solver files for each newly added case
    
        system_file_paths (dict): List of paths leading to mesh, schemes, time step and outfil writing files for each newly added case
    
    """
    current_dir = os.getcwd()
    template_dir_steps = "\\foamfiles\\counterFlowFlame2D\\template_case\\" # template case folder
    step_0 = "0" # zero folder
    step_system = "system"
    step_constant = "constant"
    
    template_case_directory = current_dir + template_dir_steps
    
    zero_folder = template_case_directory + step_0
    system_folder = template_case_directory + step_system
    constant_folder = template_case_directory + step_constant
    
    # Empty file paths within new case directories
    zero_file_paths = []
    constant_file_paths = []
    system_file_paths = []
    
    # Loop through case paths, and copy/paste into the 
    x = 0 # looping index
    while x < len(full_case_paths):
        # Template source directories
        zero_source = zero_folder
        system_source = system_folder
        constant_source = constant_folder
        
        # destination files---copy the entire tree into the new case file folders
        zero_destination = full_case_paths[x] + "\\" + step_0
        system_destination = full_case_paths[x] + "\\" + step_system
        constant_destination = full_case_paths[x] + "\\" + step_constant
        copytree(zero_source, zero_destination) # copying file to cases
        copytree(system_source, system_destination)
        copytree(constant_source, constant_destination)
        
        # Append file path lists
        zero_file_paths.append(zero_destination)
        system_file_paths.append(system_destination)
        constant_file_paths.append(constant_destination)
        
        x = x + 1
        
    print('zero file paths')
    print(zero_file_paths)
        
    print('constant file paths')
    print(constant_file_paths)
        
    print('system file paths')
    print(system_file_paths)

    return zero_file_paths, constant_file_paths, system_file_paths
    

def edit_details_files(zero_file_paths, v_boundary_strings):
    """
    Open and edit the newly created 0 case files. Edit the empty details file with the velocity strings
    
    Args:
    
        zero_file_paths (dict): List of paths leading to initial condition files for each newly added case
        
        v_boundary_strings (dict): Velocity strings to be added to details files for respective case
    
    Returns:
        None
    
    
    """

    
    details_step = "\\details" # step from zero folder to details file
    x = 0 # looping index
    while x < len(zero_file_paths):
        # loop through the details files and and write the corresponding v_boundary_strings
        details_file = zero_file_paths[x] + details_step
        with open(details_file, 'w+') as f:
            f.write('Velocity' +'\n')
            f.write(v_boundary_strings[x])
        x = x + 1
        

def edit_iterative_boundary_conditions(zero_file_paths, constant_file_paths, system_file_paths, v_boundary_strings):
    """
    Args:
        zero_file_paths (dict): List of paths leading to initial condition files for each newly added case
        
        v_boundary_strings (dict): Velocity strings to be added to details files for respective case
            
        constant_file_paths (dict): List of paths leading to solver files for each newly added case
    
        system_file_paths (dict): List of paths leading to mesh, schemes, time step and outfil writing files for each newly added case
    

    """
    # comparable to edit_boundary_conditions from the run_surrounding_cases module
    # NEGATIVE data for the LHS
    # The position for the beginning of the secondary air condition RHS (0 0.1 0) is 986
    RHS_pos = 893
    U_step = "\\U" # step from zero folder to details file
    x = 0 # looping index
    while x < len(zero_file_paths):
        # loop through the details files and and write the corresponding v_boundary_strings
        U_file = zero_file_paths[x] + U_step
        U_RHS_str = "(0 " + v_boundary_strings[x] + " 0);"
        U_LHS_str = "(0 " + "-" + v_boundary_strings[x] + " 0);"
        
        with open(U_file, '+r') as f:
            f.seek(RHS_pos) 
            f.write("    ")
            f.write("Secondary_air_RHS" +'\n')
            f.write("    ")
            f.write("{" + '\n')
            f.write("    ")
            f.write("type" + " " + "fixedValue;" + '\n')
            f.write("    ")
            f.write("value" + " " + "uniform" + " " + U_RHS_str + '\n')
            f.write("    ")
            f.write("}" + '\n')
            f.write('\n')
            f.write("    ")
            f.write("Secondary_air_LHS" +'\n')
            f.write("    ")
            f.write("{" + '\n')
            f.write("    ")
            f.write("type" + " " + "fixedValue;" + '\n')
            f.write("    ")
            f.write("value" + " " + "uniform" + " " + U_LHS_str + '\n')
            f.write("    ")
            f.write("}" + '\n')
        x = x + 1



    
    
    
    
    
    
