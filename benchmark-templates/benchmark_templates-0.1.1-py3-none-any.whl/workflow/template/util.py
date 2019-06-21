# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helper methods to read argument values for template parameters from standard
input. These methods are primarily intended to be used by a command line version
of the reproducible benchmark engine.
"""

from __future__ import print_function

from benchtmpl.io.files.base import FileHandle
from benchtmpl.io.scanner import Scanner



def read(parameters, scanner=None):
    """Read values for each of the template parameters using a given input
    scanner. If no scanner is given values are read from standard input.

    Returns a dictionary of argument values that can be passed to the workflow
    execution engine to run a parameterized workflow.

    Parameters
    ----------
    parameters: list(benchtmpl.workflow.parameter.base.TemplateParameter)
        List of workflow template parameter declarations
    scanner: benchtmpl.io.scanner.Scanner
        Input scanner to read parameter values

    Returns
    -------
    dict
    """
    sc = scanner if not scanner is None else Scanner()
    arguments = dict()
    for para in parameters:
        # Skip nested parameter
        if not para.parent is None:
            continue
        if para.is_list():
            raise ValueError('lists are not supported yet')
        elif para.is_record():
            # A record can only appear once and all record children have
            # global unique identifier. Thus, we can add values for each
            # of the children directly to the arguments dictionary
            for child in para.children:
                val = read_parameter(child, sc, prompt_prefix='  ')
                if not val is None:
                    arguments[child.identifier] = val
        else:
            val = read_parameter(para, sc)
            if not val is None:
                arguments[para.identifier] = val
    return arguments



def read_parameter(para, scanner, prompt_prefix=''):
    """Read value for a given template parameter declaration. Prompts the
    user to enter a value for the given parameter and returns the converted
    value that was entered by the user.

    Parameters
    ----------
    para: benchtmpl.workflow.parameter.TemplateParameter
        Workflow template parameter declaration

    Returns
    -------
    bool or float or int or string or list
    """
    done = False
    while not done:
        done = True
        print(prompt_prefix + para.prompt(), end='')
        try:
            if para.is_bool():
                return scanner.next_bool(default_value=para.default_value)
            elif para.is_file():
                filename = scanner.next_file(default_value=para.default_value)
                return FileHandle(filepath=filename)
            elif para.is_float():
                return scanner.next_float(default_value=para.default_value)
            elif para.is_int():
                return scanner.next_int(default_value=para.default_value)
            else:
                return scanner.next_string(default_value=para.default_value)
        except ValueError as ex:
            print(ex)
            done = False
