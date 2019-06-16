# Standard library
from typing import List, Dict

# third party
import numpy as np

# Local imports
from rewardify._util import Singleton

from rewardify.env import EnvironmentConfig

from rewardify.models import User, Pack, Reward

from rewardify.rarity import Rarity

from rewardify.adapters import RewardParametersAdapter, PackParametersAdapter

from rewardify.backends.base import AbstractBackend


# #######################
# BUSINESS LOGIC WRAPPERS
# #######################


def rarity_filter(rarity: str):
    def __callable(reward: dict):
        return reward['rarity'] == rarity
    return __callable


def available_packs() -> List[Dict]:
    """
    Returns a list of dicts, where each dict describes on of the available packs, defined in the config file:
    The dicts contain the following keys:
    name: String name of the pack
    cost: Integer gold cost
    description: string description
    1: A list with four float values describing the rarity probability distribution of that slot
    2: A list with four float values describing the rarity probability distribution of that slot
    3: A list with four float values describing the rarity probability distribution of that slot
    4: A list with four float values describing the rarity probability distribution of that slot
    5: A list with four float values describing the rarity probability distribution of that slot

    CHANGELOG

    Added 14.06.2019

    :return:
    """
    config = EnvironmentConfig.instance()
    packs_list = []
    for name, parameters in config.PACKS.items():
        packs_list.append({**parameters, **{'name': name}})
    packs_list.sort(key=lambda x: x['cost'], reverse=True)
    return packs_list


def available_rewards() -> List[Dict]:
    """
    Returns a list with dicts, each dict describing an available reward, which was defined in the backend
    The dicts contain the following keys:
    - name: String name of the reward
    - cost: Integer amount of dust, which the reward costs
    - recycle: Integer amount of dust one gets, when the reward is recycled
    - description: String description of the reward
    - rarity: The string identified for the rarity of the reward can be 'common', 'uncommon', 'rare' and
    'legendary'

    CHANGELOG

    Added 12.06.2019

    :return:
    """
    config = EnvironmentConfig.instance()
    rewards_list = []
    for name, parameters in config.REWARDS.items():
        rewards_list.append({**parameters, **{'name': name}})
    return rewards_list


def available_rewards_by_rarity():
    """
    Returns a dict, whose keys are the string rarity identifiers and the items are lists containing dicts describing
    the available rewards of that rarity, that were defined in the config file.
    The dicts contain the following keys:
    - name: String name of the reward
    - cost: Integer amount of dust, which the reward costs
    - recycle: Integer amount of dust one gets, when the reward is recycled
    - description: String description of the reward
    - rarity: The string identified for the rarity of the reward can be 'common', 'uncommon', 'rare' and
    'legendary'
    The list are sorted by the dust cost of the rewards in descending order.

    CHANGELOG

    Added 12.06.2019

    Changed 14.06.2019
    Added a sorting statement for the lists, so that they will be sorted by the their cost

    :return:
    """
    rewards = available_rewards()
    reward_dict = {}
    for rarity in Rarity.RARITIES:
        filtered_rewards = list(filter(rarity_filter(rarity), rewards))

        # 14.06.2019
        # As this function might be used to display the rewards to the user on the front end it will be useful to
        # have the entries be sorted by the cost
        filtered_rewards.sort(key=lambda x: x['cost'], reverse=True)

        reward_dict[rarity] = filtered_rewards

    return reward_dict


def open_pack(username: str, pack_name: str):
    """
    Given a user by its username and the name of a pack type, which the user owns, this function will open that pack
    for the user. This means it will evaluate the slot probabilities for all 5 slots of the pack. Based on these
    probabilities 5 rewards are randomly chosen from the set of available rewards. These rewards will be added to the
    user. The pack will be removed, as it has been used up.

    CHANGELOG

    Added 12.06.2019

    :param username:
    :param pack_name:
    :return:
    """
    user = User.get(User.name == username)
    pack = user.get_packs(pack_name)[0]

    rarity_reward_map = available_rewards_by_rarity()

    for i in range(1, 6, 1):
        slot = getattr(pack, f'slot{i}')
        rarity = slot.choice()
        reward = np.random.choice(rarity_reward_map[rarity], 1)[0]
        parameters_adapter = RewardParametersAdapter(reward['name'], reward)
        user.add_reward(parameters_adapter.parameters())

    user.use_pack(pack_name)
    user.save()

# ###############
# THE MAIN FACADE
# ###############


@Singleton
class Rewardify:
    """


    Note, 12.06.2019
    Ok I am making a design choice with this facade now. My problem was choosing between if I want to use the username
    as the parameter to all the methods of this class or do I want to use User objects. Because using just the name
    to identify the user is obviously more SOC, because whoever uses the facade doesnt have to directly interact with
    the model layer, for simple operations at least. But the user object has to be queried every time, which is more
    inefficient. I am doing it anyways, because efficiency wont be an issue with a small scale program like this
    anyways, plus one could implement caching later on if it does get a problem. So ill be acting by the theorem
    "dont overenginieer from the beginning"

    CHANGELOG

    Added 10.06.2019

    Changed 15.06.2019
    Added the method "exists_user" which returns the boolean value of a user of that name exists in the database.
    Added multiple methods for dealing with rewards including the buying, using and recycling

    """
    CONFIG: EnvironmentConfig = EnvironmentConfig.instance()

    def __init__(self):
        pass

    # ENVIRONMENTAL INFORMATION
    # -------------------------

    @classmethod
    def available_rewards_by_rarity(cls) -> Dict[str, List]:
        """
        Returns a dict, whose keys are the string rarity identifiers and the items are lists containing dicts describing
        the available rewards of that rarity, that were defined in the config file.
        The dicts contain the following keys:
        - name: String name of the reward
        - cost: Integer amount of dust, which the reward costs
        - recycle: Integer amount of dust one gets, when the reward is recycled
        - description: String description of the reward
        - rarity: The string identified for the rarity of the reward can be 'common', 'uncommon', 'rare' and
        'legendary'
        The list are sorted by the dust cost of the rewards in descending order.

        CHANGELOG

        Added 12.06.2019

        :return:
        """
        return available_rewards_by_rarity()

    @classmethod
    def available_rewards(cls) -> List[Dict]:
        """
        Returns a list with dicts, each dict describing an available reward, which was defined in the backend
        The dicts contain the following keys:
        - name: String name of the reward
        - cost: Integer amount of dust, which the reward costs
        - recycle: Integer amount of dust one gets, when the reward is recycled
        - description: String description of the reward
        - rarity: The string identified for the rarity of the reward can be 'common', 'uncommon', 'rare' and
        'legendary'

        CHANGELOG

        Added 12.06.2019

        :return:
        """
        return available_rewards()

    @classmethod
    def available_packs(cls) -> List[Dict]:
        """
        Returns a list of dicts, where each dict describes on of the available packs, defined in the config file:
        The dicts contain the following keys:
        name: String name of the pack
        cost: Integer gold cost
        description: string description
        1: A list with four float values describing the rarity probability distribution of that slot
        2: A list with four float values describing the rarity probability distribution of that slot
        3: A list with four float values describing the rarity probability distribution of that slot
        4: A list with four float values describing the rarity probability distribution of that slot
        5: A list with four float values describing the rarity probability distribution of that slot

        CHANGELOG

        Added 14.06.2019

        :return:
        """
        return available_packs()

    # USER MANAGEMENT
    # ---------------

    def user_check_password(self, username: str, password: str) -> bool:
        """
        Returns true, if the given password is the password of the user with the given username and false otherwise

        CHANGELOG

        Added 10.06.2019

        :param username:
        :param password:
        :return:
        """
        user = self.get_user(username)
        # The "password" field of a user object is a special "PasswordHash" object, which offers the method check to
        # perform a password check. A direct comparison wont work, since only a hash is saved in the database
        return user.password.check(password)

    def create_user(self, username: str, password: str):
        """
        Creates a new user with the given username and password. Initializes gold and dust with 0

        CHANGELOG

        Added 10.06.2019

        :param username:
        :param password:
        :return:
        """
        user = User(
            name=username,
            password=password,
            gold=0,
            dust=0
        )
        user.save()

    def exists_user(self, username: str):
        """
        Returns the boolean value of whether or not a user with the given username exists

        CHANGELOG

        Added 15.06.2019

        :param username:
        :return:
        """
        query = User.select().where(User.name == username)
        # Of course, when there is a result to the above query, a User object has been found and thus, the user exists
        return len(query) != 0

    # DATABASE MODELS
    # ---------------

    def get_user(self, username: str) -> User:
        """
        Returns the User object for the user with the given username

        CHANGELOG

        Added 10.06.2019

        :param username:
        :return:
        """
        query = User.select(User).where(User.name == username)
        user = query[0]
        return user

    # USER INFORMATION
    # ----------------

    # USER PACK MANAGEMENT
    # --------------------

    def user_open_pack(self, username: str, packname: str):
        """
        Opens a pack of the given packname type from the given users inventory.
        This means, that according to the packs probability distribution 5 new rewards will be added to the users
        inventory, while the pack is being removed.
        If the user does not posses a pack of that type, this method will raise a LookupError.

        CHANGELOG

        Added 12.06.2019

        :raise: LookupError

        :param username:
        :param packname:
        :return:
        """
        user = self.get_user(username)

        # The method "open_pack" of the user model expects a list of all the parameter dicts for all the available
        # rewards, so we have to create that first
        reward_parameters = self.available_rewards_parameters()

        user.open_pack(packname, reward_parameters)
        user.save()

    def user_buy_pack(self, username: str, packname: str):
        """
        Buys a pack of the type with the given packname for the given user.
        This means, that the gold cost of the pack is removed from the users inventory and a pack of that type is added
        If the user does not have enough gold, this method will raise a PermissionError

        CHANGELOG

        Added 12.06.2019

        :raise: PermissionError

        :param username:
        :param packname:
        :return:
        """
        user = self.get_user(username)
        pack_config = self.CONFIG.PACKS[packname]

        # With this adapter we convert the config information about the pack into a dict, which can be directly
        # unpacked into the model constructor, which is needed by the user.by_pack() method
        parameters_adapter = PackParametersAdapter(packname, pack_config)
        pack_parameters = parameters_adapter.parameters()

        user.buy_pack(pack_parameters)
        user.save()

    def user_get_packs(self, username: str) -> List[Pack]:
        """
        Returns a list of Pack objects from the given users inventory

        CHANGELOG

        Added 12.06.2019

        :param username:
        :return:
        """
        user = self.get_user(username)
        return user.packs

    def user_get_packs_by_name(self, username: str) ->Dict[str, List]:
        """
        Returns a dict, whose keys are the names of different pack types and the values are Pack objects of that type
        from the given users inventory

        CHANGELOG

        Added 14.06.2019

        :param username:
        :return:
        """
        user = self.get_user(username)
        return user.get_packs_by_name()

    # USER REWARD MANAGEMENT
    # ----------------------

    def user_use_reward(self, username: str, rewardname: str):
        """
        Given the type name of one of the rewards in the given users inventory, this method will use the reward for the
        user, which means the effect will be evaluated and the the instance will be deleted.
        If the user does not own a reward of the given type, a LookupError will be risen.

        CHANGELOG

        Added 15.06.2019

        Changed 16.06.2019
        Fixed a bug, where changes made by the effect of the reward would be overwritten by calling the save method
        of an unchanged user instance.

        :raise: LookupError

        :param username:
        :param rewardname:
        :return:
        """
        user = self.get_user(username)
        user.use_reward(rewardname)

        # 16.05.2019
        # NOTE! Getting the user here again (which means reloading it from the database) is super important. Because
        # the "use_reward" method makes changes to the database, which would be overwritten if a save() method on an
        # instance without these changes would be called
        user = self.get_user(username)
        user.save()

    def user_buy_reward(self, username: str, rewardname: str):
        """
        Given the name of an available reward this method will buy one instance of that type for the given user.
        If the there is no reward type of the given name, the method will raise a KeyError.
        If the user does not have enough dust to buy that reward, this method will raise a PermissionError

        CHANGELOG

        Added 15.06.2019

        :raise: KeyError, PermissionError

        :param username:
        :param rewardname:
        :return:
        """
        user = self.get_user(username)

        reward_config = self.CONFIG.REWARDS[rewardname]
        # The "user.buy_reward" function expects a complete parameter dict for the Reward class, this has to be created
        # first by plugging the dict from the config file for the reward type into the parameters adapter.
        # Every parameters adapter conforms to an interface, where the "parameters" method returns the parameters dict
        parameters_adapter = RewardParametersAdapter(rewardname, reward_config)
        reward_parameters = parameters_adapter.parameters()

        user.buy_reward(reward_parameters)
        user.save()

    def user_recycle_reward(self, username: str, rewardname: str):
        """
        This method will recylce one of the rewards with the given reward name in the given users inventory. This means
        that the instance of the reward will be removed from the inventory and recycled dust will be added to the inv.
        This method will raise a LookupError, when the user does not own a reward of the given type

        CHANGELOG

        Added 15.06.2019

        :raise: LookupError

        :param username:
        :param rewardname:
        :return:
        """
        user = self.get_user(username)
        user.recycle_reward(rewardname)
        user.save()

    def user_get_rewards(self, username: str) -> List[Reward]:
        """
        Returns a list of Reward objects from the given users inventory

        CHANGELOG

        Added 12.06.2019

        :param username:
        :return:
        """
        user = self.get_user(username)
        return user.rewards

    def user_get_rewards_by_name(self, username: str) -> Dict[str, List]:
        """
        Returns a dict, whose keys are the names of the reward types and the values the Reward objects from the users
        inventory of that type

        CHANGELOG

        Added 14.06.2019

        :param username:
        :return:
        """
        user = self.get_user(username)
        return user.get_rewards_by_name()

    # USER CURRENCY MANAGEMENT
    # ------------------------

    def user_get_gold(self, username: str) -> int:
        """
        Returns the integer amount of gold in the given users inventory

        CHANGELOG

        Added 12.06.2019

        :param username:
        :return:
        """
        user = self.get_user(username)
        return user.gold

    def user_get_dust(self, username: str) -> int:
        """
        Returns the integer amount of dust in the given users inventory

        CHANGELOG

        Added 12.06.2019

        :param username:
        :return:
        """
        user = self.get_user(username)
        return user.dust

    def user_add_gold(self, username: str, amount: int):
        """
        Adds the given amount of gold to the given users inventory

        CHANGELOG

        Added 12.06.2019

        :param username:
        :param amount:
        :return:
        """
        user = self.get_user(username)
        user.gold += amount
        user.save()

    def user_add_dust(self, username: str, amount: int):
        """
        Adds the given amount of dust to the given users inventory

        CHANGELOG

        Added 12.06.2019

        :param username:
        :param amount:
        :return:
        """
        user = self.get_user(username)
        user.dust += amount
        user.save()

    # BACKEND OPERATIONS
    # ------------------

    def backend_update(self):
        """
        This method performs a backend query to update the earned gold of the users.
        It does so by instantiating a new backend object (using the class specified in the config BACKEND) and calling
        the get_update() method on it

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        # The backend class to be used is set in the BACKEND attribute of the config.
        # Every backend class must implement the interface "get_update()", which will return a dict, whose keys are
        # the user names and the values are lists with dicts, each describing an action, that has earned them gold
        backend: AbstractBackend = self.CONFIG.BACKEND()
        action_dict = backend.get_update()
        for username, actions in action_dict.items():
            user = self.get_user(username)
            for action in actions:
                user.gold += action['gold']
            user.save()

    # CONFIGURATION MANAGEMENT
    # ------------------------

    def load(self):
        """
        This method loads all the config from the "config.py" file into the EnvironmentConfig object and initializes
        the database.
        NOTE: This method has to be called as the first thing in every programs execution! All following steps
        require this.

        CHANGELOG

        Added 10.06.2019

        :return:
        """
        # This method will issue the EnvironmentConfig object to read the config.py file to save all the variables
        # defined in there as class variables. This means all variables defined in config.py can be accessed through
        # the config object
        self.CONFIG.load()

        # The "init" method creates a new database object, based on what engine is specified.
        # The "connect" method will issue the database object to connect to the actual persistent representation of the
        # database (file for sqlite and server for mysql)
        self.CONFIG.database_config.init()
        self.CONFIG.database_config.connect()

    # SETTING UP / INSTALLING
    # -----------------------

    def create_tables(self):
        """
        Will create the necessary tables within the database to correctly represent the rewardify models.
        NOTE: This should only be called when the database was first created

        CHANGELOG

        Added 10.06.2019

        :return:
        """
        # All the models defined for this project are connected to the database object and this method will make the
        # database create all tables, needed to correctly represent the models
        self.CONFIG.database_config.create_tables()

    # HELPER METHODS
    # --------------

    def available_rewards_parameters(self):
        """
        This method will return a list of the parameter dicts of all the available rewards

        CHANGELOG

        Added 12.06.2019

        :return:
        """
        rewards = []
        for name, config in self.CONFIG.REWARDS.items():
            parameter_adapter = RewardParametersAdapter(name, config)
            rewards.append(parameter_adapter.parameters())

        return rewards
