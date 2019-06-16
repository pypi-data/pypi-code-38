# Standard library
from typing import Union

# Third party
from peewee import Field


class Rarity(object):
    """
    Instances of this object represent the rarity of a reward.
    There are four different rarities (listed in ascending magnitude): COMMON, UNCOMMON, RARE, LEGENDARY.
    A rarity object can be created using theses string names or the int indices 1, 2, 3, 4

    CHANGELOG

    Added 09.06.2019
    """
    # CLASS ATTRIBUTES / GLOBAL VARIABLES
    # -----------------------------------

    COMMON = 'common'
    UNCOMMON = 'uncommon'
    RARE = 'rare'
    LEGENDARY = 'legendary'

    RARITIES = [
        COMMON,
        UNCOMMON,
        RARE,
        LEGENDARY
    ]

    DEFAULT_VALUE = COMMON

    # These dicts exist to convert a string rarity representation to its integer format and the other way around.
    # This conversion is for example needed, when an integer is passed to the constructor or, when two rarities are
    # supposed to be compared with GREATER or LOWER
    INTEGER_MAP = {
        1: COMMON,
        2: UNCOMMON,
        3: RARE,
        4: LEGENDARY,
    }
    STRING_MAP = {
        COMMON:     1,
        UNCOMMON:   2,
        RARE:       3,
        LEGENDARY:  4,
    }

    # INSTANCE CONSTRUCTION
    # ---------------------

    def __init__(self, value: Union[str, int]):
        """
        The constructor.

        CHANGELOG

        Added 09.06.2019

        :param value:
        """
        self.value = self.DEFAULT_VALUE

        # Depending on what type of value is being passed to the constructor, we simply pass them along to their
        # individual methods to be processed (modifying the 'value' attribute of the object
        if isinstance(value, str):
            self._init_string(value)
        else:
            self._init_int(int(value))

    def _init_string(self, value: str):
        """
        This method is being called by the constructor, when a string is passed to it, it will check if the string
        has the right format and assign the correct rarity to "value" if it does, otherwise raise a ValueError

        CHANGELOG

        Added 09.06.2019

        :raises: ValueError

        :param value:
        :return:
        """
        # Passing a string as the value should be case insensitive, thus we only use the lower case version of
        # whatever string has been passed
        value_lower = value.lower()
        if value_lower in self.RARITIES:
            self.value = value_lower
        else:
            raise ValueError('The given string "%s" is not a rarity!' % value)

    def _init_int(self, value: int):
        """
        This method is being called by the constructor, when a integer is passed to it, it will check if the int is
        one of the possible rarity id's and assign the according rarity to "self.value", raises ValueError otherwise.

        CHANGELOG

        Added 09.06.2019

        :raises: ValueError

        :param value:
        :return:
        """
        # In the static attribute "INTEGER_MAP" all possible integer values, representing a rarity value are listed as
        # the keys. If a integer is passed that does not equate to a rarity an exception is risen-
        if value in self.INTEGER_MAP.keys():
            self.value = self.INTEGER_MAP[value]
        else:
            raise ValueError('The given integer "%s" is not a rarity!' % value)

    # MAGIC METHODS
    # -------------

    def __str__(self):
        """
        When the str() method is called on the object, it will return the string identifier for the given rarity
        :return:
        """
        return self.value

    def __int__(self):
        """
        When the int() function is called on the object it will return the int id for the given rarity
        :return:
        """
        return self.STRING_MAP[self.value]

    def __eq__(self, other):
        return int(self) == int(Rarity(other))

    def __gt__(self, other):
        return int(self) > int(Rarity(other))

    def __ge__(self, other):
        return int(self) >= int(Rarity(other))

    def __lt__(self, other):
        return int(self) < int(Rarity(other))

    def __le__(self, other):
        return int(self) <= int(Rarity(other))


class RarityField(Field):
    """
    This is a custom field for the database models, which saves a rarity object (most likely to be used as the
    rarity of a reward)

    CHANGELOG

    Added 09.06.2019
    """
    field_type = 'integer'

    def db_value(self, value):
        """
        This method is called when a python model object is to be saved into the database. This method derives the
        integer representation of a given rarity.
        The rarity field can be assigned a string and int identifier of a rarity or a rarity object directly

        CHANGELOG

        Added 09.06.2019

        :param value:
        :return:
        """
        # Coming from the "realm of python" we have to get the integer representation of the rarity object.
        # To enable the usage of setting strings to a rarity field also, we first create a new Rarity object from
        # the passed value and then insert the integer representation of that into the database
        rarity = Rarity(value)
        return int(rarity)

    def python_value(self, value):
        """
        This method is called, when a object is being loaded from the database. It converts the integer representation
        of the rarity into a Rarity object, which is then set as the attribute of the models instance.

        CHANGELOG

        Added 09.06.2019

        :param value:
        :return:
        """
        # We need to convert the value, which is coming from the database into a "Rarity" object to be used in the
        # python program
        return Rarity(value)
