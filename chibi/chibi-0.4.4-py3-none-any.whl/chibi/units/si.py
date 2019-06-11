from .base import Unit
from .prefix import (
    Yotta, Zetta, Exa, Peta, Tera, Giga, Mega, Kilo, Hecto,
    Deca, Base, Centi, Mili, Micro, Nano, Pico, Femto, Atto,
    Zepto, Yocto )


class Metre( Unit ):
    name = 'metre'
    symbol = 'm'
    valid_prefix = (
        Yotta, Zetta, Exa, Peta, Tera, Giga, Mega, Kilo,
        Hecto, Deca, Base, Centi, Mili, Micro, Nano, Pico,
        Femto, Atto, Zepto, Yocto )


class Gram( Unit ):
    name = 'gram'
    symbol = 'g'
    valid_prefix = (
        Yotta, Zetta, Exa, Peta, Tera, Giga, Mega, Kilo,
        Hecto, Deca, Base, Centi, Mili, Micro, Nano, Pico,
        Femto, Atto, Zepto, Yocto )
