from django.db import models
import json


class Header( models.Model ):
    key = models.CharField( max_length=128 )
    value_str = models.TextField( blank=True )

    class Meta:
        abstract = True

    def save( self, *args, **kw ):
        self.value = self.value
        super().save( *args, **kw )

    @property
    def value( self ):
        try:
            value = self._value
        except AttributeError:
            try:
                value = json.loads( self.value_str )
            except ( ValueError, TypeError ):
                value = self.value_str
        return value

    @value.setter
    def value( self, value ):
        if isinstance( value, str ):
            self.value_str = value
            self._value = value
        else:
            self.value_str = json.dumps( value )
            self._value = value

    def __str__( self ):
        return "{}: {}".format( self.key, self.value )

    def __repr__( self ):
        return "Header( key='{}' value={} )".format( self.key, self.value )

    def __eq__( self, other ):
        if not isinstance( other, Header ):
            return False
        return self.key == other.key and self.value == self.value
