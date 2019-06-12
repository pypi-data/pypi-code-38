# -*- coding: utf-8 -*-
"""
Created on Tue May 14 11:23:19 2019

@author: Lee
"""

"""Goal is to run the surrounding 4 models based on the geometry input:
    The surrounding 4 models will have varying secondary air flow rate:
    25%, 50%, 125%, 150%. 
    The output will be static, and will be used to compare the 100% secondary airflow model
"""
import os
from os import path


# Input velocity
U_100 = 100 #m/s ---> to achieve 0.033 m3/s

def compute_velocities(U_100):
    """Compute the secondary air flow rates (25-150%) based on the 100% airflow rate"""
    quarter_scale = 0.25 # 25 percent scale
    half_scale = 0.50 # half scale
    five_quarter_scale = 1.25 # adding 25% to U
    six_quarter_scale = 1.5 # adding 50% to U
    
    # Surrounding velocities RHS
    U_25_RHS = U_100*quarter_scale
    U_50_RHS = U_100*half_scale
    U_100_RHS = U_100
    U_125_RHS = U_100*five_quarter_scale
    U_150_RHS = U_100*six_quarter_scale
    
    # Surrounding velocities LHS
    U_25_LHS = -1*U_100*quarter_scale
    U_50_LHS = -1*U_100*half_scale
    U_100_LHS = -1*U_100
    U_125_LHS = -1*U_100*five_quarter_scale
    U_150_LHS = -1*U_100*six_quarter_scale
    
    # format RHS velocities as strings with max length 5
    U_25_RHS_str = str(U_25_RHS)[:5]
    U_50_RHS_str = str(U_50_RHS)[:5]
    U_100_RHS_str = str(U_100_RHS)[:5]
    U_125_RHS_str = str(U_125_RHS)[:5]
    U_150_RHS_str = str(U_150_RHS)[:5]
    
    # format LHS velocities as strings with max length 5
    U_25_LHS_str = str(U_25_LHS)[:6]
    U_50_LHS_str = str(U_50_LHS)[:6]
    U_100_LHS_str = str(U_100_LHS)[:6]
    U_125_LHS_str = str(U_125_LHS)[:6]
    U_150_LHS_str = str(U_150_LHS)[:6]

    return U_25_RHS_str, U_50_RHS_str, U_100_RHS_str, U_125_RHS_str, U_150_RHS_str, U_25_LHS_str, U_50_LHS_str, U_100_LHS_str, U_125_LHS_str, U_150_LHS_str


def locate_directories():
    """Locate the directories for the 100% and all surrounding cases"""
    # Get the current working directory --should be the StoveOpt one
    current_working_dir = os.getcwd() # absolute path of current working direcrtory
    print("here is your current WD:" + current_working_dir)
    
    # Steps from the StoveOpt parent folder to the counterFlowFlame2D folder
    dir_steps = "/foamfiles/counterFlowFlame2D/"
    
    # Extra steps to the various cases
    step_25 = "case_25/"
    step_50 = "case_50/"
    step_100 = "case_100/"
    step_125 = "case_125/"
    step_150 = "case_150/"
    
    # Full filepaths for the various cases
    path_25 = current_working_dir + dir_steps + step_25
    path_50 = current_working_dir + dir_steps + step_50
    path_125 = current_working_dir + dir_steps + step_125
    path_150 = current_working_dir + dir_steps + step_150
    path_100 = current_working_dir + dir_steps + step_100
    
    # return the 
    return path_100, path_25, path_50, path_125, path_150


def locate_zero_files(path_100, path_25, path_50, path_125, path_150):
    """locate and return the full path of the boundary condition velocity files for each of the five cases"""
    # path step for the zero folder
    zero_step = "0/"
    
    # Full respective paths for the zero folders
    path_0_100 = path_100 + zero_step
    path_0_25 = path_25 + zero_step
    path_0_50 = path_50 + zero_step
    path_0_125 = path_125 + zero_step
    path_0_150 = path_150 + zero_step
    
    # filenames for the velocity boundary conditions
    fname_0_100 = path_0_100 + "U"
    fname_0_25 = path_0_25 + "U"
    fname_0_50 = path_0_50 + "U"
    fname_0_125 = path_0_125 + "U"
    fname_0_150 = path_0_150 + "U"
    
    return fname_0_100, fname_0_25, fname_0_50, fname_0_125, fname_0_150, path_0_100, path_0_25, path_0_50, path_0_125, path_0_150


def write_velocity_files(U_25_RHS_str, U_50_RHS_str, U_100_RHS_str, U_125_RHS_str, U_150_RHS_str, U_25_LHS_str, U_50_LHS_str, U_100_LHS_str, U_125_LHS_str, U_150_LHS_str, path_0_100, path_0_125, path_0_150, path_0_25, path_0_50):
    """Create the details file for the surrounding cases, and write the velocities in line two"""
    fname = "details" # Filename
    
    file_25_path = path_0_25
    file_50_path = path_0_50
    file_100_path = path_0_100
    file_125_path = path_0_125
    file_150_path = path_0_150
    
    details_file_25 = file_25_path + fname
    details_file_50 = file_50_path + fname
    details_file_100 = file_100_path + fname
    details_file_125 = file_125_path + fname
    details_file_150 = file_150_path + fname
    
    with open(details_file_25, 'w+') as f:
        f.write('Velocity' +'\n')
        f.write(U_25_RHS_str)
    
    with open(details_file_50, 'w+') as f:
        f.write('Velocity' +'\n')
        f.write(U_50_RHS_str)
       
    with open(details_file_100, 'w+') as f:
        f.write('Velocity' +'\n')
        f.write(U_100_RHS_str)
    
    with open(details_file_125, 'w+') as f:
        f.write('Velocity' +'\n')
        f.write(U_125_RHS_str)
    
    with open(details_file_150, 'w+') as f:
        f.write('Velocity' +'\n')
        f.write(U_150_RHS_str)
    
    return details_file_25, details_file_50, details_file_100, details_file_125, details_file_150


def edit_boundary_conditions(fname_0_100, fname_0_25, fname_0_50, fname_0_125, fname_0_150):
    """Open each of the boundary condition files and insert the velocity strings into the respective files"""
    
    #LC: might have to add in some functionality to ensure the pre-existing values are shorter than the overwrite
    
    # The position for the beginning of the secondary air condition RHS (0 0.1 0) is 986
    RHS_pos = 893
    
    # Creating full strings for each surrounding case RHS
    U_RHS_25 = "(0 " + U_25_RHS_str + " 0);"
    U_RHS_50 = "(0 " + U_50_RHS_str + " 0);"
    U_RHS_100 = "(0 " + U_100_RHS_str + " 0);"
    U_RHS_125 = "(0 " + U_125_RHS_str + " 0);"
    U_RHS_150 = "(0 " + U_150_RHS_str + " 0);"
    
    
    # This is a problem---need to find the length of the string added and solve for the position of the next inlet
    # The position for the beginning of the secondary air condition LHS (0 -0.1 0) is 1098
    LHS_pos = 1098

    # Creating full strings for each surrounding case LHS    
    U_LHS_25 = "(0 " + U_25_LHS_str + " 0);"
    U_LHS_50 = "(0 " + U_50_LHS_str + " 0);"
    U_LHS_100 = "(0 " + U_100_LHS_str + " 0);"
    U_LHS_125 = "(0 " + U_125_LHS_str + " 0);"
    U_LHS_150 = "(0 " + U_150_LHS_str + " 0);"
    
    # Write the RHS inlet first
    with open(fname_0_100, 'r+') as f:
        f.seek(RHS_pos) 
        f.write("    ")
        f.write("Secondary_air_RHS" +'\n')
        f.write("    ")
        f.write("{" + '\n')
        f.write("    ")
        f.write("type" + " " + "fixedValue;" + '\n')
        f.write("    ")
        f.write("value" + " " + "uniform" + " " + U_RHS_100 + '\n')
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
        f.write("value" + " " + "uniform" + " " + U_LHS_100 + '\n')
        f.write("    ")
        f.write("}" + '\n')
        
    with open(fname_0_25, 'r+') as f:
        f.seek(RHS_pos) 
        f.write("    ")
        f.write("Secondary_air_RHS" +'\n')
        f.write("    ")
        f.write("{" + '\n')
        f.write("    ")
        f.write("type" + " " + "fixedValue;" + '\n')
        f.write("    ")
        f.write("value" + " " + "uniform" + " " + U_RHS_25 + '\n')
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
        f.write("value" + " " + "uniform" + " " + U_LHS_25 + '\n')
        f.write("    ")
        f.write("}" + '\n')
        
    
    with open(fname_0_50, 'r+') as f:
        f.seek(RHS_pos) 
        f.write("    ")
        f.write("Secondary_air_RHS" +'\n')
        f.write("    ")
        f.write("{" + '\n')
        f.write("    ")
        f.write("type" + " " + "fixedValue;" + '\n')
        f.write("    ")
        f.write("value" + " " + "uniform" + " " + U_RHS_50 + '\n')
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
        f.write("value" + " " + "uniform" + " " + U_LHS_50 + '\n')
        f.write("    ")
        f.write("}" + '\n')

    with open(fname_0_125, 'r+') as f:
        f.seek(RHS_pos) 
        f.write("    ")
        f.write("Secondary_air_RHS" +'\n')
        f.write("    ")
        f.write("{" + '\n')
        f.write("    ")
        f.write("type" + " " + "fixedValue;" + '\n')
        f.write("    ")
        f.write("value" + " " + "uniform" + " " + U_RHS_125 + '\n')
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
        f.write("value" + " " + "uniform" + " " + U_LHS_125 + '\n')
        f.write("    ")
        f.write("}" + '\n')
    
    with open(fname_0_150, 'r+') as f:
        f.seek(RHS_pos) 
        f.write("    ")
        f.write("Secondary_air_RHS" +'\n')
        f.write("    ")
        f.write("{" + '\n')
        f.write("    ")
        f.write("type" + " " + "fixedValue;" + '\n')
        f.write("    ")
        f.write("value" + " " + "uniform" + " " + U_RHS_150 + '\n')
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
        f.write("value" + " " + "uniform" + " " + U_LHS_150 + '\n')
        f.write("    ")
        f.write("}" + '\n')
        
    # Find where to enter the next data
    # Write the LHS secondary inlet data
    return U_RHS_25, U_RHS_50, U_RHS_100, U_RHS_125, U_RHS_150, U_LHS_25, U_LHS_50, U_LHS_100, U_LHS_125, U_LHS_150
    

U_25_RHS_str, U_50_RHS_str, U_100_RHS_str, U_125_RHS_str, U_150_RHS_str, U_25_LHS_str, U_50_LHS_str, U_100_LHS_str, U_125_LHS_str, U_150_LHS_str = compute_velocities(U_100)    

path_100, path_25, path_50, path_125, path_150 = locate_directories()

fname_0_100, fname_0_25, fname_0_50, fname_0_125, fname_0_150, path_0_100, path_0_25, path_0_50, path_0_125, path_0_150 = locate_zero_files(path_100, path_25, path_50, path_125, path_150)

U_RHS_25, U_RHS_50, U_RHS_100, U_RHS_125, U_RHS_150, U_LHS_25, U_LHS_50, U_LHS_100, U_LHS_125, U_LHS_150 = edit_boundary_conditions(fname_0_100, fname_0_25, fname_0_50, fname_0_125, fname_0_150)

#Print the velocities    
print('RHS')
print(U_RHS_25 + '\n')
print(U_RHS_50 + '\n')
print(U_RHS_100 + '\n')
print(U_RHS_125 + '\n')
print(U_RHS_150 + '\n')

    
print('LHS')
print(U_LHS_25 + '\n')
print(U_LHS_50 + '\n')
print(U_LHS_100 + '\n')
print(U_LHS_125 + '\n')
print(U_LHS_150 + '\n')


import shutil
from shutil import copyfile
def replace_bc_template(fname_0_100, fname_0_25, fname_0_50, fname_0_125, fname_0_150):
    """function is only for replacing the edited files of the boundary conditions with the template"""
    # Solve template path
    master_dir = os.getcwd() # absolute path of current working direcrtory
    template_steps = "\\foamfiles\\counterFlowFlame2D\\\0_template\\"
    template_fname = "U_template"
    template_path = master_dir + template_steps + template_fname
    
    # Replaces the U in the case files with empty template. leaves template in the template folder too  (copy)
    copyfile(template_path, fname_0_100)
    copyfile(template_path, fname_0_25)
    copyfile(template_path, fname_0_50)
    copyfile(template_path, fname_0_125)
    copyfile(template_path, fname_0_150)
    
# Running cases:
    




