from chibi.fancy.is_type import is_number
from chibi.units.prefix import Base


class Unit:
    name = 'abstract'
    symbol = 'abstract'
    valid_prefix = ( Base, )

    def __init__( self, value ):
        self.value = value
        self.prefix = Base

    def __str__( self ):
        return '{value}{prefix}{symbol}'.format(
            value=self.value * self.prefix.factor,
            symbol=self.symbol, prefix=self.prefix.symbol )

    def __repr__( self ):
        return '{cls}( {value} )'.format( str( self.__class__ ), str( self ) )

    def __add__( self, other ):
        if is_number( other ):
            return self.__class__( self.value + other )
        raise NotImplementedError(
            "cannot subtract no numbers, you send a {}".format(
                type( other ) ) )

    def __sub__( self, other ):
        if is_number( other ):
            return self.__class__( self.value - other )
        raise NotImplementedError(
            "cannot subtract no numbers, you send a {}".format(
                type( other ) ) )

    def __mul__( self, other ):
        if is_number( other ):
            return self.__class__( self.value * other )
        raise NotImplementedError(
            "cannot subtract no numbers, you send a {}".format(
                type( other ) ) )

    def __truediv__( self, other ):
        if is_number( other ):
            return self.__class__( self.value / other )
        raise NotImplementedError(
            "cannot subtract no numbers, you send a {}".format(
                type( other ) ) )

    def __floordiv__( self, other ):
        if is_number( other ):
            return self.__class__( self.value // other )
        raise NotImplementedError(
            "cannot subtract no numbers, you send a {}".format(
                type( other ) ) )

    def __pow__( self, other ):
        if is_number( other ):
            return self.__class__( self.value ** other )
        raise NotImplementedError(
            "cannot subtract no numbers, you send a {}".format(
                type( other ) ) )

    def __mod__( self, other ):
        if is_number( other ):
            return self.__class__( self.value % other )
        raise NotImplementedError(
            "cannot subtract no numbers, you send a {}".format(
                type( other ) ) )

    def __radd__( self, other ):
        return self + other

    def __rsub__( self, other ):
        return self - other

    def __rmul__( self, other ):
        return self * other

    def __rtruediv__( self, other ):
        return self / other

    def __rfloordiv__( self, other ):
        return self // other

    def __rpow__( self, other ):
        return self ** other
