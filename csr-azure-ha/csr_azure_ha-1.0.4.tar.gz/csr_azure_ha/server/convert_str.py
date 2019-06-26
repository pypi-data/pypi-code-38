'''
This module provides functions to take a string and try to interpret it
as a variable.

This module is intended to be imported into another module.
But, to demonstrate the ability to write a module that is both standalone and
imported, this module also contains a main() function.
It will open up and read from an input file (specifed on the command line).
For each line it reads, it treats it as a value, and calls a
function to operate on the value.  The resulting value is written to an
output file (also specified on the command line).
'''

import sys

def determine_type_from_str(input_str):
    '''
    Determine the type of the input_var.
    Return a string with the name of the type:
      (int, float, boolean, list, tuple, dict, string)
    '''

    # Check if the input variable is an integer
    try:
        invar = int(input_str)
        return 'int'
    except ValueError:
        try:
            invar = float(input_str)
            return 'float'
        except ValueError:
            try:
                # See if this is a boolean
                if (('False' == input_str) or ('True' == input_str)):
                    return 'boolean'
                # Check for a list of some type
                if ((input_str.startswith('[')) and (input_str.endswith(']'))):
                    return 'list'
                if ((input_str.startswith('(')) and (input_str.endswith(')'))):
                    return 'tuple'
                if ((input_str.startswith('{')) and (input_str.endswith('}'))):
                    return 'dict'
                # Just a regular string
                return 'str'
            except:
                return 'unknown'


def convert_str_to_variable(input_str, input_type):
    '''
    Given a string and its intended input type, return a variable which is of
    the specified type
    '''
    if input_type == 'int':
        out_var = int(input_str)
    elif input_type == 'float':
        out_var =  float(input_str)
    elif input_type == 'boolean':
        if 'False' == input_str:
            out_var =  False
        elif 'True' == input_str:
            out_var = True
    elif input_type == 'list':
        # Remove the brackets surrounding the string
        substr1 = input_str.replace('[', '', 1)
        substr2 = substr1[:-1]
        new_list = substr2.rsplit(',')
        out_var = []
        for in_entry in new_list:
            # remove leading and trailing white space
            in_entry = in_entry.strip()
            # Convert the entry into its native type
            in_entry_type = determine_type_from_str(in_entry)
            out_entry = convert_str_to_variable(in_entry, in_entry_type)
            out_var.append(out_entry)
    elif input_type == 'tuple':
        # Remove the parenthesis surrounding the string
        substr1 = input_str.replace('(', '')
        substr2 = substr1.replace(')', '')
        new_list = substr2.rsplit(',')
        out_var = []
        for in_entry in new_list:
            # remove leading and trailing white space
            in_entry = in_entry.strip()
            # Convert the entry into its native type
            in_entry_type = determine_type_from_str(in_entry)
            out_entry = convert_str_to_variable(in_entry, in_entry_type)
            out_var.append(out_entry)
        out_var = tuple(out_var)
    elif input_type == 'dict':
        # Remove the curly braces surrounding the string
        substr1 = input_str.replace('{', '')
        substr2 = substr1.replace('}', '')
        # Separate items into list of strings
        list_of_pairs = substr2.rsplit(',')
        # Create an empty dict
        out_var={}
        for list_entry in list_of_pairs:
            # Split the entry into a key and value
            key_value_pair = list_entry.rsplit(':')
            substr1 = key_value_pair[0].strip()
            key = substr1.replace('"', '')
            substr1 = key_value_pair[1].strip()
            value = substr1.replace('"', '')
            out_var[key] = value
    elif input_type == 'str':
        out_var = input_str
    else:
        out_var = "invalid"

    return out_var


def main(argv):
    argc = len(argv)
    if 3 != argc:
        print "Number of input arguments is incorrect"
        print "Usage: fileio inputFileName outputFileName"
        exit (-1)

    # Check that the input file exists
    with open(argv[1]) as in_fh:
        with open(argv[2], 'w') as out_fh:
            for line in in_fh:
                input_str = line.strip()
                var_type = determine_type_from_str(input_str)
                output_var = convert_str_to_variable(input_str, var_type)
                
                # Write the output variable to the output file
                out_str = str(output_var) + '\n'
                out_fh.write(out_str)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
