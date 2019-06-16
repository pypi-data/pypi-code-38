# -*- coding: utf-8 -*-
"""
Created on Sun May 19 18:18:31 2019

@author: Lee
"""

# Modules will pull all of the temperature versus time data from the original runs

# Should put the data into HDF5 tables as discussed in class

# Create a rank of the maximum average temperature (on full pot body)

# This needs to be a more dynamic module with values stored for future iteration

#Data import test: for 3 example files, pull expected first value, last value, and middle value

import os
from os import walk
from os import path
from sys import path
import numpy as np
from numpy import hstack, vstack, sort, transpose, argsort, append
import matplotlib.pyplot as plt
#import h5py

def data_import():
    """input a list of filenames to be pulled, put out an array of temperature data. search the foamfiles directory for fnames that start with case_ and tally the number for looping through the file. loop through each and pull data from the files (3) convert to numpy arrays (4) store.
    
    Args:
        None
    
    Returns:
        dir_list (dict): Dictionary of directory titles in the 'foamfiles' directory that begin with string 'case_'
    
        case_list (dir): Dictionary of case file paths. Appended iteratively with dir_list entries.
    
        length_case_list (int): Number of excecuted case files existing in foamfiles directory
    
        list_temps (array): Populated with results from probing the CFD simulation around entire pot geometry
    
        list_velocities (array): Populated with velocity values written to "details" file in individual case files


    """
    # navigate to the foamfiles directory
    current_directory = os.getcwd()
    #foamfile_steps = "foamfiles\counterFlowFlame2D\"
    #foamfile_path = current_directory + foamfile_steps
    foamfile_path = current_directory + "\\foamfiles\\counterFlowFlame2D\\"  
    dir_list = [directory for directory in os.listdir(foamfile_path) if os.path.isdir(foamfile_path+directory)]     
    print(dir_list)
    length_dir_list = len(dir_list)
    print("The length of the dir list: " + str(length_dir_list))
    detect_prefix = 'case' # look for case prefix
    
    i = 0 # for looping
    case_counter = 0
    case_list = [None] # empty vector
    print(case_list)
    k = 0 # case list indices
    while i < length_dir_list:
        if dir_list[i].startswith(detect_prefix):
            print(dir_list[i])
            #case_counter = case_counter  + 1
            case_list_append = dir_list[i]
            case_list[k] = case_list.append(str(dir_list[i]))
            print("here is k: " + str(k))
            print("here is i: " + str(i))
            
            case_list[k] = dir_list[i]
            print("case list k")
            print(case_list[k])
            k = k+1
            #print(case_list, sep = ", ")
        i = i+1
    
    # remove the final entry of the case_list vector
    case_list_length = len(case_list)
    print("case_list_length")
    print(case_list_length)
    omitted_value= case_list.pop(case_list_length-1)
    print("omitted value")
    print(omitted_value)
    print("Updated case list")
    print(case_list)
    
    # extract and go read data from each of the files
    """(1) Loop through the case_list produced, (2) pull the strings and 
    (3) add to the correct file extension. (4) open and read the data in.
    (5) create tables in numpy (potentially). (6) return the arrays in the overall function"""
    
    length_case_list = len(case_list)
    print("case list length: " + str(length_case_list))
    j = 0
    Temps = []
    Velocities = [] # reading in the 25-150 velocities
    list_temps = []
    list_velocities = []
    while j < length_case_list:
        fname = str(case_list[j]) # pull the case file name
        dir_steps = "\\postProcessing\\probes\\0\\"
        U_dir_steps = "\\0\\"
        U_fname = "details"
        Temp_fname = "T"
        full_path = foamfile_path + fname + dir_steps + Temp_fname # this will need to be edited for a more advanced file loc
        U_full_path = foamfile_path + fname + U_dir_steps + U_fname # varies for the cases (fname)
        with open(U_full_path, 'r') as f:
            f.seek(10) # position 10 is the beginning of line 2
            Velocity = f.readlines() # read line 2nd line
            print("Here is your velocity")
            print(Velocity) # seems to be working
            globals()['Velocities%s' % j] = Velocity # putting this into the Velocity matrix, renaming based on j to match cases
            list_velocities.append(globals()['Velocities%s' % j])

        globals()['Temps%s' % j] = np.loadtxt(fname = full_path)
        list_temps.append(globals()['Temps%s' % j])
        j = j+1
    print("here are the list temps: ")
    print(list_temps)
    print(Temps1)
    type_Temps1 = type(Temps1)
    print(type_Temps1)
    shape_Temp1 = Temps1.shape
    print("Temps1 size (rows by cols): " + str(shape_Temp1))
    print("Here is the velocity matrix for case 1")
    print(Velocities0) # solid
    
    # Concatenate all the temperatures
    """while the index is under the length of case list (# of temp vars) 
            add the temperature arrays to a list  (list temps)"""
    
    # Create list of the arrays
    """Temp_array_list = []
    while x < length_case_list:"""
    
    # Validates the list_temp is a group of the arrays    
    first_temp_list_entry = list_temps[0]   
    print("This is the 0-entry in the list_temps situaton")
    print(first_temp_list_entry)
    print("Velocity matrix")
    print(list_velocities)
    return dir_list, case_list, length_case_list, list_temps, list_velocities

#dir_list, case_list, length_case_list, list_temps, list_velocities = data_import()


def average_pot_temperature(list_temps, length_case_list, list_velocities, case_list):
    """
    Compute average temperatures of each of the case temperature arrays previously extracted with data_import()
    
    Args:
        dir_list (dict): Dictionary of directory titles in the 'foamfiles' directory that begin with string 'case_'
    
        case_list (dir): Dictionary of case file paths. Appended iteratively with dir_list entries.
    
        length_case_list (int): Number of excecuted case files existing in foamfiles directory
    
        list_temps (array): Populated with results from probing the CFD simulation around entire pot geometry
    
        list_velocities (array): Populated with velocity values written to "details" file in individual case files

    Returns:
        
        new_recarr (array): Numpy array where column 1 is case title (str), second column is velocites for respective case, and third column is computed average pot temperature for specific case
    
    
    """
    #(1) loop through the Temperature probe data and pull the final row of the array. The first entry is the time step associated with the final row
    # Convert the list_velocities to numpy array
    list_velocities_array = np.asarray(list_velocities)
    print("List velocities as array: ")
    print(list_velocities_array)
    
    list_velocities_array_transpose = list_velocities_array.transpose()
    
    # convert case list to array
    case_list_array_empty = np.empty([length_case_list,1], dtype = "U10")
    shape_case_list_array_empty = case_list_array_empty.shape
    print("Shape case list array empty: ")
    print(case_list_array_empty)
    
    l = 0
    while l < length_case_list:
        case_list_array_empty[l] = case_list[l]
        l = l +1
        print("case list array empty")
        print(case_list_array_empty)
        #case_list_array = np.ndarray.transpose(case_list_array_empty)
        case_list_array = case_list_array_empty
        print("Case list array")
        print(case_list_array)
        
    case_list_array_shape = case_list_array.shape
    print("Case list array shape")
    print(case_list_array_shape)
    
    final_temp_row = [] # empty vector to be filled  with the bottom row temperatures iteratively
    final_temp_row_matrix = [] # filling the full matrix with bottom rows iteratively
    final_temp_row_averages = [] # to be filled with the average temperatures of the final rows
    case_size = length_case_list # how many cases are included (-1 due to the 0 counting in python)
    number_properties = 3 # case#, velocity, avg temps to be included in the matrix
    
    final_temp_averages_empty = np.empty([length_case_list, 1], dtype = float)
    # Pulling the bottom row from the individual case    
    x = 0 # setting loop condition
    while x < length_case_list:
        print("list temps before error")
        print(list_temps)
        # Pull the individual temperature array, pull dimensions
        Temp_array = list_temps[x]
        print("Temp array right before the error")
        print(Temp_array)
        [rows, cols] = Temp_array.shape
        final_row = rows - 1 # navigating to the final row of temperature array
        print("Final_row")
        print(final_row)
        final_col_entry = cols # last column of the array
        first_col_entry = 1 # skip the time stamp
        
        # pull the final row of the temperature matrix
        final_temp_row = Temp_array[final_row, first_col_entry:final_col_entry]
        
        # Add to the final_temp_row_matrix
        if x == 0:
            final_temp_row_matrix = final_temp_row
        else:
            final_temp_row_matrix = np.append(final_temp_row_matrix, final_temp_row)
        
        # Compute average
        temp_average = np.average(final_temp_row)
        
        final_temp_averages_empty[x] = temp_average
        final_temp_averages = final_temp_averages_empty
        print("final temp row averages")
        print(final_temp_averages)
        
        # Checking functionality
        if x == 0:
            print("here is the temp_array")
            print(Temp_array)
            print("print final_temp_row")
            print(final_temp_row)
            print("average temperature")
            print(temp_average)
            print("final_temp_row_matrix")
            print(final_temp_row_matrix)
        else:
            print("moving on from 0")
        
        x = x +1
        print("x equals: ")
        print(x)
    # Append the temperature single column matrix with the corresponding velocities
    # Float results
    #float_cols = 2
    #results_float_matrix = np.empty(case_size, float_cols)
    
    # String column (cases)
    #string_cols = 1
    #results_string_matrix = np.empty(case_size, float_cols)
    
    # Data types for array
    dt = np.dtype([('col0', 'U10'), ('col1', float), ('col2', float)]) # first col is cases, then velocities, then temps

    
    final_temp_row_averages_array = np.asarray(final_temp_row_averages)
    print("final temp row avg array")
    print(final_temp_row_averages_array)
    final_temp_row_averages_array_transpose = final_temp_row_averages_array.transpose()
    
    new_recarr = np.empty([length_case_list,3], dtype=dt)
    new_recarr['col0'] = case_list_array
    new_recarr['col1'] = list_velocities_array
    new_recarr['col2'] = final_temp_averages
    
    print("new_recarr")
    print(new_recarr)
    
    test_value = new_recarr[2, 2]
    print("value (2,2) :")
    print(test_value)
    
    # This makes sense
    test_value_velocity = test_value[1] # take the center value from the list
    print("Test velocity pulling :")
    print(test_value_velocity)
    
    
    test_first_index = new_recarr[1]
    print("index 1:")
    print(test_first_index)
    
    test_column = new_recarr[:,1]
    print("cases: ")
    print(test_column)    
    return new_recarr

    
#new_recarr = average_pot_temperature(list_temps, length_case_list, list_velocities, case_list)
    
 
#def average_composition_outlets(list_GHG)
"""Take in a list of GHGs from a separate data import for the outlet nodes"""
    
def parse_and_sort_array(new_recarr, length_case_list):
    """
    Sort new_recarr array based on velocities, return the array with a new name
    
    Args:
        new_recarr (array): Numpy array where column 1 is case title (str), second column is velocites for respective case, and third column is computed average pot temperature for specific case
    
        length_case_list (int): Number of excecuted case files existing in foamfiles directory
    
    Returns:
        
        array_sorted (array): Numpy array. Same data as new_recarr, but sorted based on velocities (least to greatest along column 2)
    
    """
    # Algorithm:
    # (1) parse the array and create a parsed version
    
    case_vector = np.empty([length_case_list], dtype = "U10")
    velocity_vector = np.empty([length_case_list], dtype = float)
    temperature_vector = np.empty([length_case_list], dtype = float)
    
    print("shape of case vector")
    print(case_vector.shape)
    
    case_column = 0
    temperature_column = 2
    velocity_column = 1
    
    #dtype='S10,f4,f4,f4'
    # Add the cases to column 1
    # Loop through the new_recarr array, extract the case names and add them to column 1
    x = 0 # looping index
    while x < length_case_list:
        entry = new_recarr[x, 1]
        print("Entry")
        print(entry)
        case_name= str(entry[case_column])
        velocity_entry = entry[velocity_column] 
        temperature_entry = entry[temperature_column] 
        
        # Add the values to the empty vectors.
        case_vector[x] = case_name
        velocity_vector[x] = velocity_entry
        temperature_vector[x] = temperature_entry
    
        x = x + 1
        
    print("case vector")
    print(case_vector)
    
    print("velocity vector")
    print(velocity_vector)
        
    print("temperature vector")
    print(temperature_vector)
    
    parsed_new_recarr = hstack((case_vector, velocity_vector, temperature_vector))
    parsed_new_recarr_no_case_transposed = vstack((transpose(velocity_vector), transpose(temperature_vector)))
    parsed_new_recarr_no_case = vstack((velocity_vector,temperature_vector))
    
    print("parsed new recarr after column assignments")
    print(parsed_new_recarr)
    
    print("parsed new recarr, no cases, not transposed")
    print(parsed_new_recarr_no_case)
    
    print("shape of parsed new recarr after vectors added")
    print(parsed_new_recarr_no_case.shape)
    
    
    """print("shape of parsed new recarr, no cases, transpose")
    print(parsed_new_recarr_no_case_transposed.shape)"""
    
    #arr[arr[:, 1].argsort()]
    
    array_transpose = transpose(parsed_new_recarr_no_case)
    print("array transposed")
    print(array_transpose)
    
    array_sorted = array_transpose[array_transpose[:,0].argsort()]
    print("array sorted")
    print(array_sorted)

    return array_sorted

#array_sorted = parse_and_sort_array(new_recarr)


    

def evaluate_optimal(array_sorted, length_case_list):
    """
    The function evaluates the temperature and velocity data, and uses the information to identify where the optimals live within the range analayzed
    
    Args:
    
        array_sorted (array): Numpy array of sorted velocities (column 1), and average pot temperatures (column 2) 
    
        length_case_list (int): Number of excecuted case files existing in foamfiles directory

    
    Returns:
    
        T_max (float): Maximum average pot temperature of all analyzed cases within foamfiles directory
                
        velocity_max (float): Secondary air flow velocity associated with maximum average pot temperature
        
        T_max_index (int): Index associated with maximum temperature.
        
        velocity_column (array): Column array with case velocities
        
        temperature_column (array): Column array with average temperatures

    
    """
    
    # Find maximum temperature
    Temp_col = 1 # column with temperature data
    velocity_col = 0 # column with the velocity data
    
    
    # Find the maximum average temperature
    T_max = np.max(array_sorted[:,1]) # second column of the sorted array
    #T_max_index = np.where(temperature_vector == T_max)
    T_max_index = np.argmax(array_sorted[:,1])
    print("Maximum Temperature: ")
    print(T_max)
    print("Index with maximum temperature: ")
    print(T_max_index)
    
    # finding cases and velocites associated with maximum temperatures
    velocity_max = array_sorted[:,0][T_max_index]
    print("velocity_max")
    print(velocity_max)
    
    print("max velocity entry: ")
    print(velocity_max)
    
    # velocity column
    velocity_column = array_sorted[:,0]
     
    # temperature column
    temperature_column = array_sorted[:,1]
    

    return T_max, velocity_max, T_max_index, velocity_column, temperature_column
    

#T_max, velocity_max, T_max_index, velocity_column, temperature_column = evaluate_optimal(array_sorted, length_case_list)


def plot_variables(array_sorted, T_max, velocity_max, T_max_index, velocity_column, temperature_column):
    """
    Args:
        T_max (float): Maximum average pot temperature of all analyzed cases within foamfiles directory
                
        velocity_max (float): Secondary air flow velocity associated with maximum average pot temperature
        
        T_max_index (int): Index associated with maximum temperature.
        
        velocity_column (array): Column array with case velocities
        
        temperature_column (array): Column array with average temperatures

        array_sorted (array): Numpy array of sorted velocities (column 1), and average pot temperatures (column 2) 

    Returns:
        None
    """
    #fig, axs = plt.subplots(1, 3, figsize=(5,5)) # figure with multiple plots

    plt.figure(1)
    plt.scatter(velocity_column, temperature_column) # Temperature versus velocity
    plt.title("Temperature versus Case No.")
    plt.xlabel("Seconday Air Average Flow Velocity")
    plt.ylabel("Average Pot Temperature (Celsius)")
    plt.show()
     
    
#plot_variables(array_sorted, T_max, velocity_max, T_max_index, velocity_column, temperature_column)

def compute_neighboring_velocities(array_sorted, T_max, velocity_max, T_max_index, length_case_list, velocity_column, temperature_column):
    """
    Use the maximum data solved for previously to compute 4 new neighboring velocities
    
    Args:
        T_max (float): Maximum average pot temperature of all analyzed cases within foamfiles directory
                
        velocity_max (float): Secondary air flow velocity associated with maximum average pot temperature
        
        T_max_index (int): Index associated with maximum temperature.
        
        velocity_column (array): Column array with case velocities
        
        temperature_column (array): Column array with average temperatures

        array_sorted (array): Numpy array of sorted velocities (column 1), and average pot temperatures (column 2) 

    Returns:
            
        v_cases_total_vector (array): Numpy array listing four velocities to be added to the case queue
        
    
    """
    # Algorithm ==>
    # sort the new_recarr array
    # (1) Find the location of the maximum velocity within the case list
    # (2) Solve for 4 additional velocities with the following logic:
        # (a) If the maximum temp is based on an interior velocity value, add two new velocities greater than and lesser than the max
        # (b) If the max temp is associated with the lower limit velocity, compute three greater velocities, and one lesser
        # (c) If the maximum temp is associated with the maximum velocity in the list, compute 3 lesser velocities, and one greater
    
    # empty four velocity addition
    v_cases_added = np.empty([4,1], dtype = float)
    shape_v_cases_added = v_cases_added.shape
    print("shape of the added velocity vector")
    print(shape_v_cases_added)
    
    # (a) interior logic
    if (T_max_index != 0 and T_max_index != length_case_list):
        # 2 new velocities on either side of interior
        print("MAXIMUM TEMP IS WITHIN THE INTERIOR OF THE DESIGN SPACE")
        lower_velocity = velocity_column[T_max_index - 1]
        upper_velocity = velocity_column[T_max_index + 1]
        velocity_spacing = velocity_column[T_max_index] - lower_velocity
        num_values_between = 2 # number of velocities on each side of maximum
        delta_V = velocity_spacing/(num_values_between+1) # spacing
        # Lesser velocities
        v_1 = velocity_max - delta_V
        v_2 = velocity_max - 2*delta_V
        
        # greater velocities
        v_3 = velocity_max + delta_V
        v_4 = velocity_max + 2*delta_V
        
        v_cases_added[0,0] = v_1
        v_cases_added[1,0] = v_2
        v_cases_added[2,0] = v_3
        v_cases_added[3,0] = v_4
        print("Interior V-cases added")
        print(v_cases_added)
        v_cases_total_vector = v_cases_added
    
    if T_max_index == 0:
        print("MAXIMUM TEMP IS ON THE LOWER LIMIT OF THE DESIGN SPACE")
        # Lower limit maximum velocity--make sure we don't approach zero on the lower side
        # Greater side
        upper_velocity = velocity_column[T_max_index + 1]
        num_values_greater = 3
        velocity_spacing = upper_velocity - velocity_column[T_max_index]
        delta_V = velocity_spacing/(num_values_greater+1) # spacing on the greater side
        v_1 = velocity_max + delta_V
        v_2 = velocity_max + 2*delta_V
        v_3 = velocity_max + 3*delta_V
        
        # lesser side---halfway between zero and minimum velocity
        velocity_spacing_lower = velocity_max - 0
        num_values_lesser = 1
        delta_V_lower = velocity_spacing_lower/(num_values_lesser + 1)
        v_4 = velocity_max - delta_V_lower
        
        v_cases_added[0,0] = v_1
        v_cases_added[1,0] = v_2
        v_cases_added[2,0] = v_3
        v_cases_added[3,0] = v_4
        print("LOWER LIMIT V-cases added")
        print(v_cases_added)
        v_cases_total_vector = v_cases_added
    
    if T_max_index == length_case_list:
        print("MAXIMUM TEMP IS ON THE UPPER LIMIT OF THE DESIGN SPACE")
        lower_velocity = velocity_column[T_max_index - 1]
        num_values_lesser = 3
        velocity_spacing = velocity_column[T_max_index] - lower_velocity
        delta_V = delta_V = velocity_spacing/(num_values_lesser+1) # spacing on the lower side
        v_1 = velocity_max - delta_V
        v_2 = velocity_max - 2*delta_V
        v_3 = velocity_max - 3*delta_V
        
        # Greater side -- simply adding the delta_V
        v_4 = velocity_max + delta_V
        
        v_cases_added[0,0] = v_1
        v_cases_added[1,0] = v_2
        v_cases_added[2,0] = v_3
        v_cases_added[3,0] = v_4
        print("UPPER LIMIT V-cases added")
        print(v_cases_added)
        v_cases_total_vector = v_cases_added
        
    return v_cases_added, v_cases_total_vector


