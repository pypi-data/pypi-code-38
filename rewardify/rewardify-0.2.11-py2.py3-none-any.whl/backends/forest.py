# standard library
import datetime
import os
import re
import json

from typing import Dict, List
from collections import defaultdict

# third party
import pandas as pd

# local

from rewardify.env import EnvironmentConfig

from rewardify.backends.base import AbstractBackend, CheckConfigMixin


class ForestCSVFile:
    """
    This object represents one of the CSV files from the forest app.

    CHANGELOG

    Added 13.06.2019
    """

    COLUMN_NAMES = [
        'Start Time',
        'End Time',
        'Tag',
        'Note',
        'Tree Type',
        'Is Success'
    ]

    # The pandas function, which parses the CSV takes a dict, which assigns data types to the columns. Here we make
    # sure that the "Is Success" column is parsed as boolean values
    PANDAS_DATA_TYPES = {
        'Start Time':       str,
        'End Time':         str,
        'Tag':              str,
        'Note':             str,
        'Tree Type':        str,
        'Is Success':       bool
    }

    # The list of the column names to be parsed as datetime objects has to be passed separately to the
    # function, which parses the CSV file.
    PANDAS_DATETIME_COLUMNS = [
        'Start Time',
        'End Time'
    ]

    def __init__(self, path: str):
        """
        Constructor.

        CHANGELOG

        Added 13.06.2019

        :param path:
        """
        self.path = path
        self.content = self.load()

        # Tha pandas utility for csv parsing is superior to the std "csv" module, as it has auto detection of column
        # names and datatype parsing.
        # A pandas "DataFrame" object makes it significantly easier to handle the data as well, by providing a query
        # method for example.
        self.data_frame = pd.read_csv(
            path,
            dtype=self.PANDAS_DATA_TYPES,
            parse_dates=self.PANDAS_DATETIME_COLUMNS
        )

    def load(self):
        """
        Opens the file specified by "self.path" and returns the string content

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        with open(self.path, "r+") as file:
            return file.read()

    def get_dicts_after(self, date_time: datetime.datetime) -> List[Dict]:
        """
        Returns a list of dicts, where the dicts represent one activity within the csv file. Although only those
        activities are represented, whose starting time is bigger than the given date time (so the ones that have
        occurred after).
        Each dict contains the two keys:
        - duration: The integer duration of the activity
        - tag: the tag of the tree

        :param date_time:
        :return:
        """
        data_frame = self.data_frame.loc[self.data_frame['Start Time'] > date_time]
        return self.get_dicts_from_dataframe(data_frame)

    def get_dicts(self) -> List[Dict]:
        """
        Returns a list of dicts, with one dict per activity / tree within the csv file. Each dict contains the two keys:
        - duration: The integer duration in minutes
        - tag: The tag of the tree

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        return self.get_dicts_from_dataframe(self.data_frame)

    def get_last_start_time(self):
        """
        Returns the pandas Timestamp object for the start time of the last activity

        CHANGELOG

        Added 16.06.2019
        :return:
        """
        return self.data_frame['Start Time'].max()

    # HELPER METHODS
    # --------------

    @classmethod
    def get_dicts_from_dataframe(cls, data_frame: pd.DataFrame) -> List[Dict]:
        """
        Given a data frame, that has been derived from one of forests CSV files, this method extracts a list of dicts
        from it, where the dicts offer an alternative light weight representation of the activity. Each dict represents
        one tree / activity and only contains two keys "duration" for the duration in minutes and the string "tag".

        CHANGELOG

        Added 13.06.2019

        :param data_frame:
        :return:
        """
        tree_dicts = []
        for index, row in data_frame.iterrows():
            duration = cls.calculate_duration(row['Start Time'], row['End Time'])
            tree_dict = {
                'tag': row['Tag'],
                'duration': duration
            }
            tree_dicts.append(tree_dict)

        return tree_dicts

    @classmethod
    def calculate_duration(cls, start_time, end_time) -> int:
        """
        Given a start time and a end time (as pandas Datetime objects) this method will return the duration between the
        two points in time as an integer value for the minutes.

        CHANGELOG

        Added 13.06.2019

        :param start_time:
        :param end_time:
        :return:
        """
        # Using the subtraction on two Datetime objects creates a "Timedelta" object, which does not contain a direct
        # porperty "minutes", only "seconds". So the minutes have to be calculated from the seconds first
        time_delta: pd.Timedelta = end_time - start_time
        minutes = int(time_delta.seconds / 60)
        return minutes


class ForestBackend(CheckConfigMixin, AbstractBackend):

    EXPECTED_CONFIG = [
        'FOREST_BACKEND_PATH',
        'FOREST_BACKEND_SETTINGS'
    ]

    # This is the name of the file, which will contain the json information about, where the last update process of
    # the backend has left of, aka the info about which trees are new and for which gold has already been granted
    STATE_FILE_NAME = 'last_trees.json'

    # INSTANCE CONSTRUCTION
    # ---------------------

    def __init__(self):
        """
        The constructor.

        CHANGELOG

        Added 13.06.2019
        """
        # First we need an instance of the config, because the config contains all the configuration for the backend
        # as well.
        self.config: EnvironmentConfig = EnvironmentConfig.instance()
        # This method will check if all the variables from "expected_config()" are actually in the config environment
        # and raises a ModuleNotFoundError if not. After it we can assume the variables exist
        self.check_config()

        self.folder_path = self.config.FOREST_BACKEND_PATH
        # This will be a dict, whose keys are the user names from rewardify and the values are dicts, which define
        # their forest user name and their gold preferences for different tree tags.
        self.user_settings = self.config.FOREST_BACKEND_SETTINGS

        # This method will iterate the base folder and find all the relevant csv files.
        self.csv_files: List[ForestCSVFile] = []
        self.load_csv_files()

        # This method will create a dict, whose keys are the user names for the forest app and the values are the
        # user names for rewardify
        self.forest_user_map = self.get_forest_user_mapping()

        self.state = self.load_state()

    def load_csv_files(self):
        """
        This method will walk through the folder specified in "self.folder_path" and create a new ForestCSVFile object
        from each ".csv" file it finds, which it then appends to the "self.csv_files" list.

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        self.csv_files = []
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if '.csv' in file:
                    path = os.path.join(root, file)
                    # The ForestCSVFile is a wrapper class, which simplifies the csv parsing and provides easy access
                    # methods for the information that are most relevant to the backend
                    csv_file = ForestCSVFile(path)
                    self.csv_files.append(csv_file)
            # Without a break here "os.walk" would start to iterate through sub folders as well
            break

    def load_state(self):
        """
        This function loads the state file from the file system and returns the state dict. The state dict is a dict,
        which contains the string names of the rewardify users as the keys and the pandas Timestamp objects for the
        last tree, that has been accounted for during the previous run of the backend as values.

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        # If the file does not already exists, we are going to create it first
        file_path = self.get_state_file_path()
        if not os.path.exists(file_path):
            self.save_state(self._default_state())

        with open(file_path, mode='r') as file:
            state = json.load(file, object_hook=self._date_hook)

        return state

    # HELPER METHODS
    # --------------

    def calculate_gold(self, username: str, tag: str, duration: int) -> int:
        """
        Given the username, whose settings to be used, the tag string and the duration of the activity in minutes, this
        method will calculate the gold, which has been earned for the activity.

        CHANGELOG

        Added 13.06.2019

        :param username:
        :param tag:
        :param duration:
        :return:
        """
        # The user has specified "period" in the settings dict, this is the timespan in minutes, for which he wants to
        # get all the gold values, that he has specified.
        # So by getting the relation of the actual duration to this period we get the multiplier with which to multiply
        # the base value of the gold
        period = self.user_settings[username]['period']
        gold_multilpier = duration / period

        # The user only specifies the gold value for some possible tags, all other tags will give the default amount
        # by creating a default dict we can avoid the user of an if statement, because if the tag is not a key, the
        # default value will be returned
        tag_gold_map = defaultdict(lambda: self.user_settings[username]['default'])
        tag_gold_map.update(self.user_settings[username])

        base_gold = tag_gold_map[tag]
        gold = int(base_gold * gold_multilpier)
        return gold

    def get_forest_user_mapping(self):
        """
        Returns a dict, which maps the user names of rewardify to the user names for the forest app. The keys of the
        dict will be the strin user names for forest and the values the string user names for rewardify

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        forest_user_map = {}
        for username, settings in self.user_settings.items():
            forest_name = settings['name']
            forest_user_map[forest_name] = username
        return forest_user_map

    def get_new_user_activities(self) -> Dict:
        """
        This method returns a dict, whose keys are the user names of the rewardify users and the values are lists with
        activity dicts associated with those users. An activity dict has two keys: "tag" for the kind of tree that was
        planted and "duration" for the time in minutes the activity lasted.
        The activities are new in the sense, that the lists only contain dicts for those trees that have been planted
        AFTER the last tree, that has been processed during the previous run of the backend

        CHANGELOG

        Added 13.06.2019

        Changed 16.06.2019
        The state now gets updated after calling this method, which means a second call to get new methods will return
        an empty list, as the activities are not new anymore, when there was a previous call

        :return:
        """
        user_activities = {}
        user_csv_files = self.get_user_csv_files()
        for user_name, csv_files in user_csv_files.items():
            activities = []
            for csv_file in csv_files:  # type: ForestCSVFile
                # From the state dict we get the pandas Timestamp object, which marks the starting time of the last
                # activity, that has been accounted for.
                # Thus we can get the new actovities as all the activities AFTER that last one
                last_start_time = self.state[user_name]
                activities += csv_file.get_dicts_after(last_start_time)
                self.state[user_name] = csv_file.get_last_start_time()

            user_activities[user_name] = activities

        return user_activities

    def get_user_csv_files(self):
        """
        Returns a dict, whose keys are the user names of the rewardify users and the values are the ForestCSVFile
        objects associated with them.

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        user_csv_files = defaultdict(list)
        for csv_file in self.csv_files:
            forest_name = self.forest_name_from_path(csv_file.path)
            user_name = self.forest_user_map[forest_name]
            user_csv_files[user_name].append(csv_file)
        return user_csv_files

    def get_state_file_path(self) ->str:
        """
        Returns the string file path for the state file. This is the json file, which contains the date of the last
        tree, that has been accounted for during the last run of the backend.

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        file_path = os.path.join(self.folder_path, self.STATE_FILE_NAME)
        return file_path

    def save_state(self, state: Dict):
        """
        Given the state dict, this function will save it as the state json file.

        CHANGELOG

        Added 13.06.2019

        :param state:
        :return:
        """
        file_path = self.get_state_file_path()
        with open(file_path, mode="w") as file:
            # The self._str_hook method calls the str() function on all the values of the dict and then returns it
            # again. This is important, because the pandas Timestamp objects are not in themselves json serializable
            json.dump(self._str_hook(state), file)

    @classmethod
    def forest_name_from_path(cls, path):
        """
        Given the path string to a forest csv file, this method will extract the forest user name from that string

        CHANGELOG

        Added 13.06.2019

        :param path:
        :return:
        """
        file_name = os.path.basename(path)
        # This regex pattern extracts the string, which is between two brackets
        result = re.search(".*\((.+?)\).*", file_name)
        forest_name = result.group(1)
        return forest_name

    @classmethod
    def _date_hook(cls, json_dict: Dict) -> Dict:
        """
        This is a function, which takes a dict and attempts to convert all the values into pandas Timestamp objects
        and then returns the dict again.
        A function of this type (takes a dict, gives a dict) can be passed to the json.load() function to make a type
        conversion.

        CHANGELOG

        Added 13.06.2019

        :param json_dict:
        :return:
        """
        for key, value in json_dict.items():
            json_dict[key] = pd.to_datetime(value)
        return json_dict

    @classmethod
    def _str_hook(cls, json_dict: Dict) -> Dict:
        """
        This is a function, which takes a dict and attempts to convert all the values into strings and then returns
        teh dict again.
        A function of this type (takes a dict, gives a dict) can be passed to the json.load() function to make a type
        conversion.

        CHANGELOG

        Added 13.06.2019

        :param json_dict:
        :return:
        """
        for key, value in json_dict.items():
            json_dict[key] = str(value)
        return json_dict

    def _default_state(self):
        """
        Returns the default state dict, which dates the last successful tree at 1701.

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        last_trees = {}
        for user_name in self.user_settings.keys():
            last_trees[user_name] = pd.to_datetime("Sat Jan 15 08:07:54 GMT+01:00 1701")
        return last_trees

    # IMPLEMENTING INTERFACE
    # ----------------------

    def get_update(self):
        """
        This is the main function for the backend, it will return a dict, whose keys are the user names and whose
        values are lists of dicts, which each describe the gold, that has been earned for a certain activity.

        CHANGELOG

        Added 13.06.2019

        Changed 16.06.2019
        The new state is being saved at the end of the run.

        :return:
        """
        update_dict = defaultdict(list)
        user_activities = self.get_new_user_activities()
        for user_name, activities in user_activities.items():
            for activity in activities:
                gold = self.calculate_gold(user_name, activity['tag'], activity['duration'])
                action_dict = {
                    'name':         'Tree',
                    'description':  activity['tag'],
                    'gold':         gold,
                    'date':         datetime.datetime.now()
                }
                update_dict[user_name].append(action_dict)

        # 16.06.2019
        # After everything is updated the new state has to be saved, so that the next call to the update function will
        # not return the ones from this run.
        self.save_state(self.state)

        return update_dict

    # IMPLEMENTING MIXIN REQUIREMENTS
    # -------------------------------

    def get_config(self):
        """
        Returns a reference to the EnvironmentConfig instance

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        return self.config

    def expected_config(self):
        """
        Returns a list with the string names of the expected config variables.

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        return self.EXPECTED_CONFIG
