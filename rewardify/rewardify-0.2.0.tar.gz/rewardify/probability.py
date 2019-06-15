# Standard library
from typing import Union, List

# Third party
import numpy as np

from peewee import Field

# Local imports
from rewardify.rarity import Rarity


class RarityProbability:
    """
    Instances of this class represent a probability distribution for the different rarity values. These probab. values
    denote the probability, that a reward of this rarity will appear from a pack.

    CHANGELOG

    Added 09.06.2019
    """
    def __init__(self,
                 common_probability: float,
                 uncommon_probability: float,
                 rare_probability: float,
                 legendary_probability: float):
        self.dict = {
            Rarity.COMMON:      common_probability,
            Rarity.UNCOMMON:    uncommon_probability,
            Rarity.RARE:        rare_probability,
            Rarity.LEGENDARY:   legendary_probability
        }

    # METHODS
    # -------

    def choice(self):
        """
        This method will make an actual random decision and return a rarity identifier (from Rarity.RARITIES) based on
        the given probability distribution of this object.

        CHANGELOG

        Added 12.06.2019

        :return:
        """
        result = np.random.choice(list(self.dict.keys()), 1, p=list(self.dict.values()))
        return result[0]

    def list(self) -> List[float]:
        """
        This method returns a list, which contains the probability values for the different rarities in ascending order
        of rarity magnitude.

        CHANGELOG

        Added 09.06.2019

        :return:
        """
        return list(self.dict.values())

    def csv(self, accuracy: int = 4) -> str:
        """
        This methods returns a string, where the four probability values are separated by commas, each value having as
        many places after the decimal point as given by the "accuracy" argument.

        EXAMPLE:
        accuracy=4
        >> "0.5000,0.2000,0.2000,0.1000"

        CHANGELOG

        Added 09.06.2019

        :param accuracy:
        :return:
        """
        # First we create a template string for converting the float numbers for each probability into strings with the
        # amount of numbers after the decimal point as specified by "accuracy"
        template = "{%s}" % ":01.{}f".format(accuracy)
        format_string = ','.join([template, template, template, template])

        # Now we use the the probability values to fill in the format string
        probabilities = self.list()
        csv_string = format_string.format(*probabilities)
        return csv_string

    def equals(self, prob):
        """
        Returns true, if this object describes the same probability distribution as the other RarityProbability object
        "prob" given (which means all the values have to be the same). Returns False otherwise

        CHANGELOG

        Added 09.06.2019

        :param prob:
        :return:
        """
        for key, value in self.dict.items():
            # If any value is found, that is not the same, the two objects are not the same
            if prob[key] != value:
                return False

        # If the above loop exited, without returning False prematurely, the two objects are equal
        return True

    # PROPERTIES
    # ----------

    # MAGIC METHODS
    # -------------

    def __len__(self):
        return len(self.dict.keys())

    def __getitem__(self, item):
        """
        This method is being called, when an "Rarity Probability" is being indexed with "item".
        It can be indexed by all the means of specifiying a rarity: correct string or int id or a Rarity object
        directly

        CHANGELOG

        Added 09.06.2019

        :param item:
        :return:
        """
        rarity = Rarity(item)
        return self.dict[str(rarity)]

    def __setitem__(self, key, value):
        """
        It can be indexed by all the means of specifiying a rarity: correct string or int id or a Rarity object
        directly

        CHANGELOG

        Added 09.06.2019

        :param key:
        :param value:
        :return:
        """
        rarity = Rarity(key)
        self.dict[str(rarity)] = float(value)

    def __eq__(self, other):
        """
        Returns true, if this object describes the same probability distribution as the other RarityProbability object
        "prob" given (which means all the values have to be the same). Returns False otherwise.
        Raises a TypeError in case one should try to compare it with any other type of object.

        CHANGELOG

        Added 09.06.2019

        :raises: TypeError

        :param other:
        :return:
        """
        if isinstance(other, RarityProbability):
            return self.equals(other)
        else:
            raise TypeError('You cannot compare a RarityProbability with anything else than objects of same type!')

    # CLASS METHODS
    # -------------

    @classmethod
    def from_iterable(cls, probabilities):
        """
        Creates a new RarityProbability object from an iterable (list or tuple), where the order of the elements is
        being interpreted as the order of the rarities in ascending order

        CHANGELOG

        Added 09.06.2019

        :param probabilities:
        :return:
        """
        return RarityProbability(*probabilities)

    @classmethod
    def from_csv(cls, string: str):
        """
        Creates new RarityProbability object from a csv string.

        CHANGELOG

        Added 09.06.2019

        :param string:
        :return:
        """
        # First we obviously get a lost of the values by splitting by the commas
        values = string.split(',')

        # These values of the list are still strings though and still need to be converted into the
        # floats
        float_values = list(map(float, values))

        # Creating a new object using these values
        return RarityProbability(*float_values)


class ProbabilityField(Field):
    """
    This is a custom field for the database models, which represents the probability distribution for the appearance of
    the different rarities of rewards in a pack slot.

    CHANGELOG

    Added 09.06.2019
    """
    # CLASS VARIABLES
    # ---------------

    # This is the error message, that is being shown, when the value of a ProbabilityField is set with a value
    # of an unsupported type
    DB_VALUE_ERROR = 'You need to pass either a list or a RarityProbability object to the ProbabilityField!'

    # This is the type of column to which this field maps in an actual database
    field_type = 'text'

    def python_value(self, value):
        # For getting the python value, we just have to create a RarityProbability from the csv text saved in the
        # database
        return RarityProbability.from_csv(value)

    def db_value(self, value):
        # First of all the value needs to be either a list, that contains 4 floats to specify the probabilities or a
        # RarityProbability object directly.
        # If it is a list we create a new RarityProbability object from that list first
        rarity_probability = self.convert_rarity_probability(value)

        # Now we create a csv string from the object, which can be saved into the text column
        return rarity_probability.csv()

    # HELPER METHODS
    # --------------

    def convert_rarity_probability(self,
                                   value: Union[RarityProbability, List[float]]
                                   ) -> RarityProbability:
        """

        :param value:
        :return:
        """
        if isinstance(value, list):
            probability = RarityProbability.from_iterable(value)
        elif isinstance(value, RarityProbability):
            probability = value
        else:
            raise ValueError(self.DB_VALUE_ERROR)

        return probability
