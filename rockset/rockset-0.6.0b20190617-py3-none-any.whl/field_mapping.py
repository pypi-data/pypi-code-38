"""
Introduction
------------
FieldMapping objects represent various transformations that apply to all
documents inserted into a collection.

Example usage
-------------
::
    from rockset import Client

    rs = Client()

    mappings = [
        rs.FieldMapping.mapping(
            name="anonymize_name"
            input_fields=[
                    {
                        rs.FieldMapping.input_fields(
                            field_name="name", if_missing="SKIP",
                            is_drop=true, param="name")
                    }
                ]
            output_field=rs.FieldMapping.output_field(
                field_name="name_anon",
                sql_expression="SHA256(:name)",
                on_error="FAIL")
            )]
    newcoll = rs.Collection.create(name="newcoll", field_mappings=mappings)
"""


class FieldMapping(object):
    def __str__(self):
        return str(vars(self))

    def __iter__(self):
        for k, v in vars(self).items():
            yield (k, v)

    @classmethod
    def mapping(cls, name, input_fields=None, output_field=None):
        """Creates a new mapping object

        Args:
            name(str): Name of the mapping
            input_fields: An Array of InputField objects
            output: An OutputField object
        """
        input_dict = [dict(f) for f in input_fields]
        output_dict = dict(output_field)
        return Mapping(
            name=name, input_fields=input_dict, output_field=output_dict
        )

    @classmethod
    def input_field(cls, field_name, param=None, if_missing=None, is_drop=None):
        """Create a new InputField object

        Args:
            field_name (str): The name of the field, parsed as a SQL qualified name
            param (str): SQL parameter name (default: same as field name. Required
                if the field name is nested)
            if_missing (str): Define the behavior if field name is missing or is NULL,
                one of:
                    "SKIP" (skip the update),
                    "PASS" (pass NULL to the update function)
                [default: "SKIP"]
            is_drop (boolean): Set to true if the input field needs to be dropped
        """
        return InputField(
            field_name=field_name,
            param=param,
            if_missing=if_missing,
            is_drop=is_drop
        )

    @classmethod
    def output_field(cls, field_name, sql_expression, on_error=None):
        """Create a new OutputField object

        Args:
            name (str): The name of the field, parsed as SQL qualified name
            value (Value): SQL expression
            on_error (str): Define the error behavior, one of:
                "SKIP" (skip output field),
                "FAIL" (fail the update)
                [default: "SKIP"]
            """
        return OutputField(
            field_name=field_name,
            sql_expression=sql_expression,
            on_error=on_error
        )


class Mapping(FieldMapping):
    def __init__(self, name, input_fields=None, output_field=None):
        self.name = name
        self.input_fields = input_fields

        if output_field is not None:
            self.output_field = output_field


class InputField:
    def __init__(self, field_name, param=None, if_missing=None, is_drop=None):
        self.field_name = field_name
        if param is not None:
            self.param = param
        if if_missing is not None:
            self.if_missing = if_missing
        if is_drop is not None:
            self.is_drop = is_drop
        return

    def __str__(self):
        return str(vars(self))

    def __iter__(self):
        for k, v in vars(self).items():
            yield (k, v)


class OutputField:
    def __init__(self, field_name, sql_expression, on_error=None):
        self.field_name = field_name
        self.value = {
            'sql': sql_expression,
        }
        if on_error is not None:
            self.on_error = on_error
        return

    def __str__(self):
        return str(vars(self))

    def __iter__(self):
        for k, v in vars(self).items():
            yield (k, v)
