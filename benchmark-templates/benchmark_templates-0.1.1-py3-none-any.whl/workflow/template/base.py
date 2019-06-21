# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""A workflow template contains a list of template parameters and a workflow
specification that contains references to template parameters.

Template parameters are common to different backends that excute a workflow. The
syntax and structure of the workflow specification is engine specific. The only
common part here is that template parameters are referenced using the $[[..]]
syntax from within the specifications.

The template parameters can be used to render front-end forms that gather user
input for each parameter. Given an association of parameter identifiers to
user-provided values, the workflow backend is expected to be able to execute
the modified workflow specification in which references to template parameters
have been replaced by parameter values.
"""

from benchtmpl.workflow.parameter.base import TemplateParameter
from benchtmpl.workflow.parameter.value import TemplateArgument

import benchtmpl.error as err
import benchtmpl.util.core as util
import benchtmpl.workflow.parameter.util as para


class TemplateHandle(object):
    """The workflow template contains a dictionary of template parameter
    declarations. Parameter declarations are keyed by their unique identifier
    in the dictionary. The template also contains the workflow specification.
    The syntax and structure of the specification is not further inspected.
    Each template has a unique identifier and an optional base directory that
    contains input files for the represented workflow.
    """
    def __init__(self, workflow_spec, identifier=None, base_dir=None, parameters=None):
        """Initialize the components of the workflow template. A ValueError is
        raised if the identifier of template parameters are not unique.

        Parameters
        ----------
        workflow_spec: dict
            Workflow specification object
        identifier: string, optional
            Unique template identifier. If no value is given a UUID will be
            assigned.
        base_dir: string, optional
            Optional path to directory on disk that contains static files that
            are required to run the represented workflow
        parameters: list(benchtmpl.workflow.parameter.base.TemplateParameter), optional
            List of workflow template parameter declarations

        Raises
        ------
        benchtmpl.error.InvalidTemplateError
        """
        self.workflow_spec = workflow_spec
        if not identifier is None:
            self.identifier = identifier
        else:
            self.identifier = util.get_unique_identifier()
        self.base_dir = base_dir
        # Add given parameter declarations to the parameter index.
        self.parameters = dict()
        if not parameters is None:
            for para in parameters:
                # Ensure that the identifier of all parameters are unique
                if para.identifier in self.parameters:
                    raise err.InvalidTemplateError('parameter \'{}\' not unique'.format(para.identifier))
                self.parameters[para.identifier] = para

    def get_argument(self, identifier, value, validate=False):
        """Get instance of the template argument class for the given parameter
        and the given value.

        Parameters
        ----------
        identifier: string
            Unique parameter declaration identifier
        value: any
            Argument value for the parameter
        validate: bool, optional
            Validate the argument value against the parameter declaration if
            set to True

        Returns
        -------
        benchtmpl.workflow.parameter.value import TemplateArgument
        """
        return TemplateArgument(
            parameter=self.get_parameter(identifier),
            value=value,
            validate=validate
        )

    def get_parameter(self, identifier):
        """Short-cut to access the declaration for a parameter with the given
        identifier.

        Parameters
        ----------
        identifier: string
            Unique parameter declaration identifier

        Returns
        -------
        dict
        """
        return self.parameters.get(identifier)

    def list_parameters(self):
        """Get a sorted list of parameter declarations. Elements are sorted by
        their index value. Ties are broken using the unique parameter
        identifier.

        Returns
        -------
        list(benchtmpl.workflow.parameter.base.TemplateParameter)
        """
        return para.sort_parameters(self.parameters.values())

    def validate_arguments(self, arguments):
        """Ensure that the workflow can be instantiated using the given set of
        arguments. Raises an error if there are template parameters for which
        the argument set does not provide a values and that do not have a
        default value defined.

        Parameters
        ----------
        arguments: dict() or set()
            Dictionary of argument values for parameters in the template

        Raises
        ------benchtmpl.error.MissingArgumentError
        """
        for para in self.parameters.values():
            if para.is_required and para.default_value is None:
                if not para.identifier in arguments:
                    raise MissingArgumentError(para.identifier)


# ------------------------------------------------------------------------------
# Helper Methods
# ------------------------------------------------------------------------------

def get_parameter_name(value):
    """Extract the parameter name for a template parameter reference.

    Parameters
    ----------
    value: string
        String value in the workflow specification for a template parameter

    Returns
    -------
    string
    """
    return value[3:-2]


def get_parameter_references(spec, parameters=None):
    """Get set of parameter identifier that are referenced in the given
    workflow specification. Adds parameter identifier to the given parameter
    set.

    Parameters
    ----------
    spec: dict
        Parameterized workflow specification
    parameters: set, optional
        Result set of parameter identifier

    Returns
    -------
    set

    Raises
    ------
    benchtmpl.error.InvalidTemplateError
    """
    # The new object will contain the modified workflow specification
    if parameters is None:
        parameters = set()
    for key in spec:
        val = spec[key]
        if isinstance(val, str):
            # If the value is of type string we test whether the string is a
            # reference to a template parameter
            if is_parameter(val):
                # Extract variable name.
                parameters.add(get_parameter_name(val))
        elif isinstance(val, dict):
            # Recursive call to get_parameter_references
            get_parameter_references(val, parameters=parameters)
        elif isinstance(val, list):
            for list_val in val:
                if isinstance(list_val, str):
                    # Get potential references to template parameters in
                    # list elements of type string.
                    if is_parameter(list_val):
                        # Extract variable name.
                        parameters.add(get_parameter_name(list_val))
                elif isinstance(list_val, dict):
                    # Recursive replace for dictionaries
                    get_parameter_references(list_val, parameters=parameters)
                elif isinstance(list_val, list):
                    # We currently do not support lists of lists
                    raise err.InvalidTemplateError('nested lists not supported')
    return parameters


def is_parameter(value):
    """Returns True if the given value is a reference to a template parameter.

    Parameters
    ----------
    value: string
        String value in the workflow specification for a template parameter

    Returns
    -------
    bool
    """
    # Check if the value matches the template parameter reference pattern
    return value.startswith('$[[') and value.endswith(']]')


def replace_args(spec, arguments, parameters):
    """Replace template parameter references in the workflow specification
    with their respective values in the argument dictionary or their
    defined default value. The type of the result is depending on the type
    of the spec object

    Returns a modified dictionary.

    Parameters
    ----------
    spec: any
        Parameterized workflow specification
    arguments: dict(benchtmpl.workflow.parameter.value.TemplateArgument)
        Dictionary that associates template parameter identifiers with
        argument values
    parameters: dict(benchtmpl.workflow.parameter.base.TemplateParameter)
        Dictionary of parameter declarations

    Returns
    -------
    type(spec)

    Raises
    ------
    benchtmpl.error.InvalidTemplateError
    """
    if isinstance(spec, dict):
        # The new object will contain the modified workflow specification
        obj = dict()
        for key in spec:
            obj[key] = replace_args(spec[key], arguments, parameters)
    elif isinstance(spec, list):
        obj = list()
        for val in spec:
            if isinstance(val, list):
                # We currently do not support lists of lists
                raise err.InvalidTemplateError('nested lists not supported')
            obj.append(replace_args(val, arguments, parameters))
    elif isinstance(spec, str) or isinstance(spec, basestring):
        obj = replace_value(spec, arguments, parameters)
    else:
        obj = spec
    return obj


def replace_value(value, arguments, parameters):
    """Test whether the string is a reference to a template parameter and (if
    True) replace the value with the given argument or default value.

    In the current implementation template parameters are referenced using
    $[[..]] syntax.

    Parameters
    ----------
    value: string
        String value in the workflow specification for a template parameter
    arguments: dict(benchtmpl.workflow.parameter.value.TemplateArgument)
        Dictionary that associates template parameter identifiers with
        argument values
    parameters: dict(benchtmpl.workflow.parameter.base.TemplateParameter)
        Dictionary of parameter declarations

    Returns
    -------
    string
    """
    # Check if the value matches the template parameter reference pattern
    if is_parameter(value):
        # Extract variable name.
        var = get_parameter_name(value)
        para = parameters[var]
        # If the parameter has a constant value defined use that value as the
        # replacement
        if para.has_constant():
            return para.get_constant()
        # If arguments contains a value for the variable we return the
        # associated value from the dictionary. Note that there is a special
        # treatment for file arguments. If case of file arguments the dictionary
        # value is expected to be a file handle. In this case we return the
        # file name as the argument value.
        if var in arguments:
            arg = arguments[var]
            if para.is_file():
                return arg.value.name
            else:
                return arg.value
        # Return the parameter default value
        return para.default_value
    else:
        return value
