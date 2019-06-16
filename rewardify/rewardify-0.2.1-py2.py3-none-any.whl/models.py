# standard library
import re

from typing import Dict, List

from collections import defaultdict

# Third party imports
import numpy as np

from peewee import DatabaseProxy
from peewee import Model
from peewee import ForeignKeyField, CharField, IntegerField, DateTimeField, TextField

# Local imports
from rewardify._util import rarity_filter

from rewardify.password import PasswordField

from rewardify.rarity import Rarity
from rewardify.rarity import RarityField

from rewardify.probability import ProbabilityField


# GENERAL SETUP
# #############


DATABASE_PROXY = DatabaseProxy()


class BaseModel(Model):
    """
    This is the abstract base class for all the models of this program. It defines the connection to a database proxy
    (a placeholder for a database), which can be bound to an actual instance of a database at runtime (when the login
    info to the database has been read from a config file possibly)

    CHANGELOG

    Added 09.06.2019
    """
    class Meta:
        database = DATABASE_PROXY


# ACTUAL MODEL CLASSES
# ####################

class User(BaseModel):
    """
    The database model to represent a user of the rewardify program

    CHANGELOG

    Added 09.06.2019
    """
    name = CharField(unique=True)
    password = PasswordField()
    gold = IntegerField()
    dust = IntegerField()

    # REWARD MANAGEMENT
    # -----------------

    def use_reward(self, reward_name: str):
        """
        Given the reward name of a type of reward in the users inventory, this method will user the reward. This means
        the reward effect will be evaluated first (if there is one) and then the instance will be deleted.

        CHANGELOG

        Added 15.06.2019

        :param reward_name:
        :return:
        """
        rewards = self.get_rewards(reward_name)
        reward = rewards[0]
        reward.use()

    def add_reward(self, reward_parameters: Dict):
        """
        Given the parameters dict for a new reward object, this method will add the specified reward to the user

        CHANGELOG

        Added 12.06.2019

        :param reward_parameters:
        :return:
        """
        # The reward parameters passed to this method are obviously still missing the "user" key, which defines to which
        # user the reward will be associated, when it is created
        reward_parameters.update({'user': self})
        reward = Reward(**reward_parameters)
        reward.save()

    def buy_reward(self, reward_parameters: Dict):
        """
        Given the parameters dict for a new Reward object, this method will buy the specified reward for the user. If
        the user does not have enough dust to buy it this method will raise a PermissionError

        CHANGELOG

        Added 12.06.2019

        :raises: PermissionError

        :param reward_parameters:
        :return:
        """
        # First we need to check if we have enough dust to buy the reward
        self.check_dust(reward_parameters['dust_cost'])

        # Now we create new pack, add it to the user and then remove the dust cost from the dust balance
        self.add_reward(reward_parameters)
        self.dust -= reward_parameters['dust_cost']

    def recycle_reward(self, reward_name: str):
        """
        Given the name of a reward type, this method will delete one of these rewards, which the user owns and add
        the recycle amount for that reward to the users dust balance.
        If the user does not own a reward of that type, LookupError will occur

        CHANGELOG

        Added 12.06.2019

        Changed 15.06.2019
        Now the recycling "operation" is not done in here, because that is none of the concern of the user object,
        instead the "recycle()" method of the Reward instance is called and the returned int amount of dust is added
        to the dust balance of the user.

        :raises: LookupError

        :param reward_name:
        :return:
        """
        rewards = self.get_rewards(reward_name)
        reward: Reward = rewards[0]
        self.dust += reward.recycle()

    def get_rewards(self, reward_name: str) -> List:
        """
        Given the name of a reward type, this method will return all reward instances of that type, which the user
        owns. If the user does not own one of this type, the method will raise a lookup error.

        CHANGELOG

        Added 12.06.2019

        :raises: LookupError

        :param reward_name:
        :return:
        """
        # Here we are getting all the rewards, that belong to this user and have the given name
        query = Reward.select(Reward, User).join(User).where(
            (User.name == self.name) &
            (Reward.name == reward_name)
        )
        if len(query) == 0:
            raise LookupError(
                "User {} does not posses rewards by the name {}".format(self.name, reward_name)
            )
        return list(query)

    def get_rewards_by_name(self) -> Dict[str, List]:
        """
        This method returns a dict, where the keys are the names of the rewards and the values are list containing the
        Reward objects from the users inventory of that reward type

        CHANGELOG

        Added 14.06.2019

        :return:
        """
        rewards_dict = defaultdict(list)
        for reward in self.rewards:
            rewards_dict[reward.name].append(reward)
        return rewards_dict

    # PACK MANAGEMENT
    # ---------------

    def add_pack(self, pack_parameters: Dict):
        """
        Given the parameters dict for a new Pack object, this method will add the specified Pack to the user

        CHANGELOG

        Added 12.06.2019

        :param pack_parameters:
        :return:
        """
        # The pack parameters passed to this method are obviously still missing the "user" key, which defines to which
        # user the pack will be associated, when it is created
        pack_parameters.update({'user': self})
        pack = Pack(**pack_parameters)
        pack.save()

    def buy_pack(self, pack_parameters: Dict):
        """
        Given the parameters dict for a new Pack object, this method will buy the pack for the user. If the user does
        not have enough gold to buy it, this method will raise a PermissionError

        CHANGELOG

        Added 12.06.2019

        :raises: PermissionError

        :param pack_parameters:
        :return:
        """
        # First we need to check if we even have enough gold to buy this.
        # In case we do not, this will raise a Permission error, otherwise do nothing
        self.check_gold(pack_parameters['gold_cost'])

        # We buy the pack by creating the pack object and assigning it to the user and then removing the gold it
        # cost from the balance
        self.add_pack(pack_parameters)
        self.gold -= pack_parameters['gold_cost']

    def open_pack(self, pack_name: str, available_rewards: List[Dict]):
        """
        Given the name of the pack type to be opened from the users inventory and a list, which will contain the
        reward parameter list for all available rewards, this method will evaluate the slot probabilities for each of
        the 5 slots and randomly pick a reward. These rewards will be added to the user and the opened pack will be
        removed.
        If the user does not own a pack of the given type, a LookupError will be risen

        CHANGELOG

        Added 12.06.2019

        :raises: LookupError

        :param pack_name:
        :param available_rewards:
        :return:
        """
        pack = self.get_packs(pack_name)[0]
        rarity_reward_map = self._available_rewards_by_rarity(available_rewards)

        for slot in pack.get_slots():
            # The "choice" method of a RarityProbability object will evaluate the probabilities and according to those
            # randomly pick and return a rarity (string)
            rarity = slot.choice()

            # When we already have a rarity, than we can get a list of all available rewards with this rarity from the
            # "rarity_reward_map". This is the second step of the random process to get the rewards. from all these
            # rewards with the same, chosen rarity one is being picked with equal probabilities
            rarity_rewards = rarity_reward_map[rarity]
            reward_parameters = np.random.choice(rarity_rewards, 1)

            # From the parameter dict, we can now add the rewards to the user directly
            self.add_reward(reward_parameters)

        # At the end we should not forget to delete the pack in question, as it was used up
        pack.delete_instance()

    def use_pack(self, pack_name: str):
        """
        Given the pack name, this method will delete one of the pack instances of the given type, which the user
        currently owns (=> using it up). If the user does not own a pack of this type. This method will raise a
        LookupError.
        NOTE!: It is important to understand, that this method does not actually perform a pack opening. To do that
        the knowledge of the configuration environment is needed, which is none of a models concern! The logic for
        actually choosing the rewards and adding them needs to be implemented in a separate function

        CHANGELOG

        Added 12.06.2019

        :raises: LookupError

        :param pack_name:
        :return:
        """
        packs = self.get_packs(pack_name)
        pack = packs[0]
        pack.delete_instance()

    def get_packs(self, pack_name: str) -> List:
        """
        Given the name of a pack type, this method will return all pack instances of that type, which the user
        owns. If the user does not own one of this type, the method will raise a lookup error.

        CHANGELOG

        Added 12.06.2019

        :raises: LookupError

        :param pack_name:
        :return:
        """
        query = Pack.select(Pack, User).join(User).where(
            (User.name == self.name) &
            (Pack.name == pack_name)
        )
        if len(query) == 0:
            raise LookupError(
                "User {} does not posse packs by the name {}".format(self.name, pack_name)
            )
        return list(query)

    def get_packs_by_name(self) -> Dict[str, List]:
        """
        This method returns a dict, where the keys are the names of different types of packs and the values are lists
        with the pack objects of these types from the users inventory

        CHANGELOG

        Added 14.06.2019

        :return:
        """
        packs_dict = defaultdict(list)
        for pack in self.packs:
            packs_dict[pack.name].append(pack)
        return packs_dict

    # CURRENCY MANAGEMENT
    # -------------------

    def check_gold(self, amount: int):
        """
        Given an amount of gold, this method checks if the user has that much gold and in case he does not it raises a
        PermissionError.

        CHANGELOG

        Added 12.06.2019

        :raises 12.06.2019

        :param amount:
        :return:
        """
        if self.gold < amount:
            raise PermissionError(
                "User {} does not have {} gold!".format(self.name, amount)
            )

    def check_dust(self, amount: int):
        """
        Given an amount of dust, this method checks if the user has that much dust and in case he does not it raises a
        PermissionError

        CHANGELOG

        Added 12.06.2019

        :raises: PermissionError

        :param amount:
        :return:
        """
        if self.dust < amount:
            raise PermissionError(
                'User {} does not habe {} dust!'.format(self.name, amount)
            )

    # HELPER FUNCTIONS
    # ----------------

    @classmethod
    def _available_rewards_by_rarity(cls, available_rewards: List[Dict]) -> Dict:
        """
        Given the list containing the parameter dicts for all available rewards, this method returns a dict, whose
        keys are the rarity indentifiers and the values are lists with all the parameter dicts of the rewards with
        that rarity

        CHANGELOG

        Added 12.06.2019

        :param available_rewards:
        :return:
        """
        mapping = {}
        for rarity in Rarity.RARITIES:
            rewards = list(filter(rarity_filter(rarity), available_rewards))
            mapping[rarity] = rewards

        return mapping


class Reward(BaseModel):
    """
    The database model to represent a reward, which a user has obtained

    CHANGELOG

    Added 09.06.2019

    Changed 15.06.2019
    Added the "recycle" method, which will delete the instance and return the amount of dust gained from the recycling.
    Added the "use" method, which will use up the reward.
    Added the "effect" text field for the new version. This field can optionally contain a special syntax, which
    specified, what effect the reward has on the rewardify system, when it is being used. As of right now two effects
    are being supported: Granting gold and dust to the user upon opening.
    """

    # DATABASE FIELDS
    # ---------------

    name = CharField()
    slug = CharField()
    description = TextField()
    dust_cost = IntegerField()
    dust_recycle = IntegerField()
    date_obtained = DateTimeField()
    rarity = RarityField()
    effect = TextField()

    user = ForeignKeyField(User, backref='rewards')

    # CONSTANTS
    # ---------

    # These regular expressions will search for any occurance of the substrings "gold(...)" and "dust(...)".
    # The result of the regular expressions will also directly exctract the substring from within the parentheses,
    # which specify the amount that has been granted by this effect
    GOLD_EFFECT_REGEX = 'gold\((.+?)\)'
    DUST_EFFECT_REGEX = 'dust\((.+?)\)'

    # INSTANCE METHODS
    # ----------------

    def use(self):
        """
        This method will use up the reward. First any possible effect of the reward will be evaluated and then the
        instance is deleted

        CHANGELOG

        Added 15.06.2019

        :return:
        """
        self.evaluate_effect()
        self.delete_instance()

    def recycle(self):
        """
        This method will recycle the reward, which means, that the instance will be deleted, but the method will return
        the integer amount of dust, that has been gained from recycling the reward

        CHANGELOG

        Added 15.06.2019

        :return:
        """
        dust_recycle = self.dust_recycle
        self.delete_instance()
        return dust_recycle

    def evaluate_effect(self):
        """
        This method evaluates the effect given in the "effect" string of the reward instance. The effect string can
        (it is an optional property of a reward) contain special syntax to describe, what kind of effect the reward has
        on the rewardify system, when it is being used. (Such as adding gold to the users balance)

        CHANGELOG

        Added 15.06.2019

        :return:
        """
        self.evaluate_dust_effect()
        self.evaluate_gold_effect()
        self.user.save()

    # EVALUATION OF THE EFFECTS
    # -------------------------

    def evaluate_gold_effect(self):
        """
        This method will evaluate the "effect" string of the reward instance to see if it contains the syntax
        "gold(...)" for a gold effect and if it does the effect is being applied by adding as much gold as specified
        in the parentheses to the users gold.
        Raises a value error if the argument within the parentheses is not an integer.

        CHANGELOG

        Added 15.06.2019

        :raise: ValueError

        :return:
        """
        try:
            effect = str(self.effect)
            result = re.search(self.GOLD_EFFECT_REGEX, effect)
            substring = result.group(1)
            amount = int(substring)
            self.user.gold += amount
        # An attribute error will occur, when the regular expression has not found anything and it is attempted to call
        # the "group(1)" method on a none type object.
        # In this case there just is no effect to be applied
        except AttributeError:
            return
        # A value error will occur, when there was this expression in the effect string, but the substring in between
        # the parentheses is not the string of an integer.
        # This is clearly a problem and thus the exception is being risen again
        except ValueError:
            raise ValueError('The substring "{}" can not be the argument of a GOLD EFFECT!'.format(substring))

    def evaluate_dust_effect(self):
        """
        This method will evaluate the "effect" string of the reward instance to see if it contains the syntax
        "dust(...)" for a dust effect and if it does, the effect is being applied by adding as much dust as specified
        in the parentheses to the users dust account.

        Raises a value error if the argument within the parentheses is not an integer.

        CHANGELOG

        Added 15.06.2019

        :raise: ValueError

        :return:
        """
        try:
            effect = str(self.effect)
            result = re.search(self.DUST_EFFECT_REGEX, effect)
            substring = result.group(1)
            amount = int(substring)
            self.user.dust += amount
        # An attribute error will occur, when the regular expression has not found anything and it is attempted to call
        # the "group(1)" method on a none type object.
        # In this case there just is no effect to be applied
        except AttributeError:
            return
        # A value error will occur, when there was this expression in the effect string, but the substring in between
        # the parentheses is not the string of an integer.
        # This is clearly a problem and thus the exception is being risen again
        except ValueError:
            raise ValueError('The substring "{}" can not be the argument of a DUST EFFECT!'.format(substring))


class Pack(BaseModel):
    """
    The database model to represent a pack, which a user has obtained

    CHANGELOG

    Added 09.06.2019
    """
    SLOT_INDICES = [1, 2, 3, 4, 5]

    name = CharField()
    slug = CharField()
    description = TextField()
    gold_cost = IntegerField()
    date_obtained = DateTimeField()
    slot1 = ProbabilityField()
    slot2 = ProbabilityField()
    slot3 = ProbabilityField()
    slot4 = ProbabilityField()
    slot5 = ProbabilityField()

    user = ForeignKeyField(User, backref='packs')

    def get_slots(self):
        """
        This will return a list which contains the RarityProbability objects for the 5 slots of this pack instance.

        CHANGELOG

        Added 12.06.2019

        :return:
        """
        slots = []
        for index in self.SLOT_INDICES:
            # This will basically return the field object of this very Pack instance for the fields in ascending
            # order
            slot = getattr(self, f'slot{index}')
            slots.append(slot)

        return slots

