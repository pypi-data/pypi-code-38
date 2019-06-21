# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helper methods for workflow template parameters."""


from benchtmpl.workflow.parameter.base import TemplateParameter

import benchtmpl.error as err
import benchtmpl.workflow.parameter.declaration as pd


def create_parameter_index(parameters, validate=True):
    """Create instances of template parameters from a list of dictionaries
    containing parameter declarations. The result is a dictionary containing the
    top-level parameters, indexed by their unique identifier.

    Parameters
    ----------
    parameters: list(dict)
        List of dictionaries containing template parameter declarations
    validate: bool, optional
        Flag indicating if given template parameter declarations are to be
        validated against the parameter schema or not.

    Returns
    -------
    dict(benchtmpl.workflow.parameter.base.TemplateParameter)

    Raises
    ------
    benchtmpl.error.InvalidTemplateError
    benchtmpl.error.UnknownParameterError
    """
    result = dict()
    for para in parameters:
        # Validate the template parameters if the validate flag is True
        if validate:
            pd.validate_parameter(para)
        # Create a TemplateParameter instance for the parameter. Keep
        # track of children for parameter that are of type DT_LIST or
        # DT_RECORD. Children are added after all parameters have been
        # instantiated.
        p_id = para[pd.LABEL_ID]
        # Ensure that the identifier of all parameters are unique
        if p_id in result:
            raise err.InvalidTemplateError('parameter \'{}\' not unique'.format(p_id))
        c = None
        if para[pd.LABEL_DATATYPE] in [pd.DT_LIST, pd.DT_RECORD]:
            c = list()
        tp = TemplateParameter(pd.set_defaults(para), children=c)
        result[p_id] = tp
    # Add parameter templates to the list of children for their
    # respective parent (if given). We currently only support one level
    # of nesting.
    for para in parameters:
        if pd.LABEL_PARENT in para:
            p_id = para[pd.LABEL_ID]
            parent = para[pd.LABEL_PARENT]
            if not parent is None:
                result[parent].add_child(result[p_id])
    return result


def sort_parameters(parameters):
    """Sort a given list of parameter declaration by the parameter index that is
    part of the parameter declaration. Parameters with the same index value are
    ordered by increasing value of their name.

    Parameters
    ----------
    parameters: list(benchtmpl.workflow.parameter.base.TemplateParameter)
        List of termplate parameters

    Returns
    -------
    list(benchtmpl.workflow.parameter.base.TemplateParameter)
    """
    return sorted(parameters, key=lambda p: (p.index, p.identifier))
