# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""stored procedure parameter class."""

from enum import Enum


class StoredProcedureParameter(object):
    """class of the representation of a SQL stored procedure parameter."""

    def __init__(self, name, value, type=None):
        """Class StoredProcedureParameter constructor.

        :param name: the name of the stored procedure parameter.
        :type name: str
        :param value: the value of the stored procedure parameter.
        :type value: str
        :param type: the type of the stored procedure parameter value,
        defaults to azureml.data.stored_procedure_parameter.StoredProcedureParameterType.String
        :type type: azureml.data.stored_procedure_parameter.StoredProcedureParameterType
        """
        self.name = name
        self.value = value
        self.type = type or StoredProcedureParameterType.String


class StoredProcedureParameterType(Enum):
    """class of the representation of a SQL stored procedure parameter type."""

    String = "String"
    Int = "Int"
    Decimal = "Decimal"
    Guid = "Guid"
    Boolean = "Boolean"
    Date = "Date"
