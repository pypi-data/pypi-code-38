from django.db import models


class Base64_field( models.CharField ):

    def pre_save( self, model_instance, add ):
        string = super().pre_save( model_instance, add )
        return string

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return value

    def to_python(self, value):
        if value is None:
            return value

        return value
