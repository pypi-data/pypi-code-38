# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Functionality to execute a function in a child process created using "spawn".

This file contains the server portion.
"""
import dill
import importlib.util
import sys


def run_server(config_file_name, input_file_name, output_file_name):
    """Run the server."""
    # Deserialize the configuration object using dill.
    with open(config_file_name, 'rb') as file:
        config = dill.load(file)

    if not isinstance(config, dict):
        raise TypeError("Invalid configuration object type.")

    # Initialize system path to match parent process configuration.
    sys.path = config['path']

    # Deserialize the input file using dill.
    with open(input_file_name, 'rb') as file:
        obj = dill.load(file)

    # Deconstruct the input into function, arguments, keywords arguments.
    if not isinstance(obj, tuple):
        raise TypeError("Invalid input data object type.")

    if len(obj) != 3:
        raise ValueError("Expected (function, args, kwargs) tuple.")

    f, args, kwargs = obj

    # Invoke the function and store the result in a (value, error) pair.
    try:
        # TODO: Currently this code assumes that the called function will already return such a pair. Need to fix.
        res = f(*args, **kwargs)
        assert isinstance(res, tuple)
        assert len(res) == 2
    except BaseException as err:
        res = (None, err)

    # Write the result to the output file using dill.
    with open(output_file_name, 'wb') as file:
        dill.dump(res, file)


# Check command-line arguments.
if len(sys.argv) != 4:
    print("Usage: spawn_server config_file input_file output_file")
else:
    # Extract configuration, input, and output file names.
    config_file_name = sys.argv[1]
    input_file_name = sys.argv[2]
    output_file_name = sys.argv[3]

    run_server(config_file_name, input_file_name, output_file_name)
