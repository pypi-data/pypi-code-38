# standard library
import datetime

from typing import Dict

# local imports
from rewardify.rarity import Rarity


# #######################
# INTERFACE SPECIFICATION
# #######################


class ModelParameterAdapterInterface:
    """
    This is an interface specifying, what a model parameter adapter has to implement.
    First of all: What is the use case of a "model parameter adapter"? Take the example of possible rewards. To the
    users available rewards are defined as a dict like structure in the config file, the keys of these dicts do not
    correlate one to one to the names of the model fields though and some model fields might even need to be computed
    from other values. This is where an adapter comes in. The dict from the config is plugged in and through
    the "parameters()" method of the adapter the complete parameters dict for the model is created, with which a model
    can be instantiated like this: "model = Model( **adapter.parameters() )"

    CHANGELOG

    Added 12.06.2019
    """

    def parameters(self) -> Dict:
        """
        This is the only method, that has to be implemented. It has to return a dict, where the keys are exactly named
        like the fields of the models and the values being the values, that were passed to the constructor of the
        adapter.

        CHANGELOG

        Added 12.06.2019

        :return:
        """
        raise NotImplementedError


# ################
# BEHAVIOUR MIXINS
# ################


class SlugAdapterMixin:
    """
    This is a behaviour mixin for parameter adapter implementations. It contains the common functionality for creating
    the slug from the plain text name of a model object.

    CHANGELOG

    Added 12.06.2019
    """
    @classmethod
    def create_slug(cls, name) -> str:
        """
        Given the name of an instance, this method will create the slug from that name, by putting it into all lower
        case and replacing the whitespaces with underscores.

        CHANGELOG

        Added 12.06.2019

        :param name:
        :return:
        """
        # The slug is being created to have a more processing friendly version of the name, which means all lower case
        # and no white spaces (these are being replaced by underscores)
        slug = name.lower()
        slug = slug.replace(' ', '_')

        return slug


# ###################
# THE ACTUAL ADAPTERS
# ###################


class RewardParametersAdapter(SlugAdapterMixin, ModelParameterAdapterInterface):
    """
    This adapter object takes the name of an available reward and its configuration dict as specified in the config
    file of the project and created a parameters dict upon calling the "parameters()" method which can be directly
    unpacked into the constructor of the Reward model class

    CHANGELOG

    Added 12.06.2019

    Changed 15.06.2019
    Made adjustments for the "effect" parameter of the Reward class in the new version
    """

    # The keys are the string names, which the user can use in the config file and the values are the constants, which
    # the code uses internally to create a new Reward object.
    RARITY_MAPPING = {
        'common':           Rarity.COMMON,
        'uncommon':         Rarity.UNCOMMON,
        'rare':             Rarity.RARE,
        'legendary':        Rarity.LEGENDARY,
    }

    # 15.06.2019
    # This default dict is needed as the effect parameter for example is OPTIONAL, which means, it does not appear in
    # every config dict for a reward, but we have to provide a default value to the database model anyways
    DEFAULT_CONFIG = {
        'description':      '',
        'rarity':           'common',
        'effect':           '',
        'cost':             0,
        'recycle':          0
    }

    def __init__(self, name: str, config: Dict):
        """
        The constructor.

        CHANGELOG

        Added 12.06.2019

        Changed 15.06.2019
        The config dict for the reward is now first being initialized with the DEFAULT_CONFIG dict and then updated
        with the actual values of the given config.
        This is to provide a default for eventually not given optional parameters (such as "effect")

        :param name:
        :param config:
        """
        self.name = name
        self.config = self.DEFAULT_CONFIG
        self.config.update(config)

    def parameters(self) -> Dict:
        """
        Returns the parameters dict for the constructor of the Reward model class

        CHANGELOG

        Added 12.06.2019

        Changed 15.06.2019
        Added the "effect" parameter, which has been introduced with the new version. The effect parameter will contain
        a string directive, which denotes which effect the reward has on the system. For example granting dust

        :return:
        """
        parameters = {
            'name':             self.name,
            'slug':             self.create_slug(self.name),
            'description':      self.config['description'],
            'rarity':           self.convert_rarity(self.config['rarity']),
            'effect':           self.config['effect'],
            'dust_cost':        self.config['cost'],
            'dust_recycle':     self.config['recycle'],
            'date_obtained':    datetime.datetime.now()
        }
        return parameters

    def convert_rarity(self, rarity: str):
        """
        Given the string name of the rarity from the config dict, this method will return the according constant,
        that will be recognized by the field as a valid identifier for one of the four rarities

        CHANGELOG

        Added 12.06.2019

        :param rarity:
        :return:
        """
        return self.RARITY_MAPPING[rarity]


class PackParametersAdapter(SlugAdapterMixin, ModelParameterAdapterInterface):
    """
    This adapter object takes the name of an available pack and its configuration dict as specified in the config
    file of the project and created a parameters dict upon calling the "parameters()" method which can be directly
    unpacked into the constructor of the Pack model class

    CHANGELOG

    Added 12.06.2019
    """

    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config

    def parameters(self):
        """
        Returns the parameters dict for the constructor of the Pack model class

        CHANGELOG

        Added 12.06.2019

        :return:
        """
        parameters = {
            'name':             self.name,
            'slug':             self.create_slug(self.name),
            'description':      self.config['description'],
            'gold_cost':        self.config['cost'],
            'slot1':            self.config['1'],
            'slot2':            self.config['2'],
            'slot3':            self.config['3'],
            'slot4':            self.config['4'],
            'slot5':            self.config['5'],
            'date_obtained':    datetime.datetime.now()
        }
        return parameters
