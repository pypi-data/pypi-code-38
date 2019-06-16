# standard library
import unittest
import os
import datetime
import json

# third party
import pandas
import pandas.api.types as ptypes

# local imports
from rewardify._util_test import RewardifyTestCase

from rewardify.backends import MockBackend, ForestBackend
from rewardify.backends.forest import ForestCSVFile

from rewardify.env import EnvironmentConfig


# #################################################################
# TESTING THE GENERAL INTERFACE FUNCTIONALITY WITH THE MOCK BACKEND
# #################################################################


class TestMockBackend(RewardifyTestCase):

    CONFIG: EnvironmentConfig = EnvironmentConfig.instance()

    SAMPLE_IMPORTS = [
        'from rewardify.backends import AbstractBackend'
    ]

    SAMPLE_DATABASE_DICT = {
        'engine': 'sqlite',
        'host': ':memory:',
        'database': '',
        'user': '',
        'password': '',
        'port': 0
    }

    SAMPLE_PACKS = [
        {
            'name':         'SamplePack',
            'description':  'shitty pack',
            'cost':         1000,
            'slot1':        [1, 0, 0, 0],
            'slot2':        [1, 0, 0, 0],
            'slot3':        [1, 0, 0, 0],
            'slot4':        [1, 0, 0, 0],
            'slot5':        [1, 0, 0, 0],
        }
    ]

    SAMPLE_REWARDS = [
        {
            'name':         'SampleReward',
            'cost':         1000,
            'recycle':      1000,
            'description':  'none',
            'rarity':       'common'
        }
    ]

    SAMPLE_BACKEND = 'MockBackend'

    SAMPLE_PLUGIN_CODE = 'MOCK_BACKEND_USERS = ["Jonas"]'

    def test_mock_creation_works(self):
        self.setup_sample()

        mock_backend = MockBackend()
        update_dict = mock_backend.get_update()
        self.assertTrue('Jonas' in update_dict.keys())
        self.assertDictEqual(MockBackend.MOCK_ACTION, update_dict['Jonas'][0])

    # HELPER METHODS
    # --------------

    def setup_sample(self):
        # Setting up the config-py file
        self.create_config(
            self.SAMPLE_IMPORTS,
            self.SAMPLE_DATABASE_DICT,
            self.SAMPLE_BACKEND,
            self.SAMPLE_REWARDS,
            self.SAMPLE_PACKS,
            self.SAMPLE_PLUGIN_CODE
        )


# ##################
# FOREST APP BACKEND
# ##################

class TestForestCSVFile(RewardifyTestCase):

    CONFIG: EnvironmentConfig = EnvironmentConfig.instance()

    SAMPLE_CSV_NAME = 'sample.csv'

    SAMPLE_CSV_CONTENT = '''"Start Time","End Time","Tag","Note","Tree Type","Is Success"
"Mon Dec 10 09:43:41 GMT+01:00 2018","Mon Dec 10 09:53:41 GMT+01:00 2018","Nicht gesetzt","","Busch","True"
"Mon Dec 10 09:54:23 GMT+01:00 2018","Mon Dec 10 10:24:23 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"
"Mon Dec 10 10:54:11 GMT+01:00 2018","Mon Dec 10 11:24:11 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"'''

    # ACTUAL TESTS
    # ------------

    def test_sample_csv_content_alignment(self):
        # We check if a TAB is in the sample string. Because i am not sure how that works with the indentation of the
        # class variable and a multiline string.
        self.assertTrue("    " not in self.SAMPLE_CSV_CONTENT)

    def test_csv_file_is_being_created(self):
        self.create_csv()
        # Checking if the file exists
        self.assertTrue(os.path.exists(self.csv_path()))
        # Content correct?
        with open(self.csv_path(), mode='r') as file:
            content = file.read()
            self.assertEqual(content, self.SAMPLE_CSV_CONTENT)

    def test_load_file_pandas_data_types(self):
        self.create_csv()

        csv_file = ForestCSVFile(self.csv_path())
        # Making sure the datetime fields are parsed as such
        self.assertTrue(ptypes.is_datetime64_ns_dtype(csv_file.data_frame.dtypes['Start Time']))
        self.assertTrue(ptypes.is_datetime64_ns_dtype(csv_file.data_frame.dtypes['End Time']))
        # Checking if the boolean "is Success" column is actually boolean
        self.assertTrue(ptypes.is_bool_dtype(csv_file.data_frame.dtypes['Is Success']))

    def test_calculating_duration(self):
        self.create_csv()

        csv_file = ForestCSVFile(self.csv_path())
        for index, row in csv_file.data_frame.iterrows():
            duration = csv_file.calculate_duration(row['Start Time'], row['End Time'])
            duration_calculated = int((row['End Time'] - row['Start Time']).seconds / 60)
            self.assertEqual(duration, duration_calculated)

    def test_get_dicts(self):
        self.create_csv()

        csv_file = ForestCSVFile(self.csv_path())

        # The dicts, which are returned by the "get_dicts" method are supposed to have to values, one for the
        # tag of the tree (which is important for how much gold per minute is granted) and the duration in minutes,
        # which the activity lasted.
        activity_dicts = csv_file.get_dicts()
        self.assertEqual(len(activity_dicts), 3)
        dict_keys = list(activity_dicts[0].keys())
        self.assertListEqual(dict_keys, ['tag', 'duration'])

    def test_get_dicts_after(self):
        self.create_csv()
        csv_file = ForestCSVFile(self.csv_path())

        # This is the date time of the second tree in the sample CSV. Which means only the last tree should turn up in
        # the list using the "_after" method!
        date_time = pandas.to_datetime("Mon Dec 10 09:54:23 GMT+01:00 2018")
        activity_dicts = csv_file.get_dicts_after(date_time)
        self.assertEqual(len(activity_dicts), 1)

    # HELPER METHODS
    # --------------

    def create_csv(self):
        path = self.csv_path()
        with open(path, mode='w+') as file:
            file.write(self.SAMPLE_CSV_CONTENT)

    def csv_path(self):
        return os.path.join(self.FOLDER_PATH, self.SAMPLE_CSV_NAME)


class TestForestBackend(RewardifyTestCase):

    # SAMPLE CONFIG FILE SETUP
    # ------------------------

    SAMPLE_IMPORTS = [
        'from rewardify.backends.forest import ForestBackend'
    ]

    SAMPLE_DATABASE_DICT = {
        'engine':   'sqlite',
        'host':     ':memory:',
        'port':     0
    }

    SAMPLE_PACKS = []
    SAMPLE_REWARDS = []

    SAMPLE_BACKEND = 'ForestBackend'

    SAMPLE_PLUGIN_CODE = '''
FOREST_BACKEND_PATH = "/tmp/rewardify"
FOREST_BACKEND_SETTINGS = {
    "Jonas": {
        "name":     "Jonas",
        "period":   60,
        "default":  1000
    },
    "Joana": {
        "name":     "LuaMia",
        "period":   30,
        "default":  10     
    },
}'''

    # SAMPLE FOREST SETUP
    # -------------------

    SAMPLE_CSV_FILES = {
        'Plants of jonseb1998@gmail.com (Jonas).csv': '''"Start Time","End Time","Tag","Note","Tree Type","Is Success"
"Mon Dec 10 16:01:22 GMT+01:00 2018","Mon Dec 10 16:31:22 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"
"Mon Dec 10 20:01:08 GMT+01:00 2018","Mon Dec 10 20:31:08 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"
"Tue Dec 11 08:15:04 GMT+01:00 2018","Tue Dec 11 09:00:04 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"
"Tue Dec 11 09:16:48 GMT+01:00 2018","Tue Dec 11 09:46:48 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"
"Tue Dec 11 10:01:44 GMT+01:00 2018","Tue Dec 11 10:41:44 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"
"Tue Dec 11 11:17:17 GMT+01:00 2018","Tue Dec 11 11:47:17 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"
        ''',
        'Plants of luamia@gmail.com (LuaMia).csv': '''"Start Time","End Time","Tag","Note","Tree Type","Is Success"
"Fri Dec 14 07:37:54 GMT+01:00 2018","Fri Dec 14 08:07:54 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"
"Fri Dec 14 08:29:21 GMT+01:00 2018","Fri Dec 14 08:59:21 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"
"Fri Dec 14 09:01:32 GMT+01:00 2018","Fri Dec 14 09:31:32 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"
"Fri Dec 14 10:13:53 GMT+01:00 2018","Fri Dec 14 10:43:53 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"
"Fri Dec 14 15:12:35 GMT+01:00 2018","Fri Dec 14 15:42:35 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"
"Sat Dec 15 09:08:42 GMT+01:00 2018","Sat Dec 15 09:18:01 GMT+01:00 2018","Nicht gesetzt","","Zeder","False"
"Sat Dec 15 09:19:09 GMT+01:00 2018","Sat Dec 15 10:14:09 GMT+01:00 2018","Nicht gesetzt","","Zeder","True"
        '''
    }

    # ACTUAL TESTS
    # ------------

    def test_forest_backend_test_case_generally_working(self):
        self.setup_sample()

        forest_backend = ForestBackend()
        csv_paths = self.get_sample_csv_paths()
        for path in csv_paths:
            self.assertTrue(os.path.exists(path))

    def test_folder_path_correct(self):
        self.setup_sample()

        forest_backend = ForestBackend()
        self.assertEqual(forest_backend.folder_path, '/tmp/rewardify')

    def test_loading_csv_files(self):
        self.setup_sample()

        forest_backend = ForestBackend()
        self.assertEqual(len(forest_backend.csv_files), 2)
        self.assertIsInstance(forest_backend.csv_files[0], ForestCSVFile)

    def test_extract_forest_name_from_csv_path(self):
        self.setup_sample()

        csv_paths = self.get_sample_csv_paths()
        forest_names = list(map(ForestBackend.forest_name_from_path, csv_paths))
        self.assertListEqual(forest_names, ['Jonas', 'LuaMia'])

    def test_create_forest_user_map(self):
        self.setup_sample()

        forest_backend = ForestBackend()
        # This method should return a dict, whose keys are the string user names for forest and the values are the
        # string user names for rewardify
        forest_user_map = forest_backend.get_forest_user_mapping()

        expected = {
            'Jonas':    'Jonas',
            'LuaMia':   'Joana'
        }
        self.assertDictEqual(forest_user_map, expected)

    def test_default_state_works(self):
        self.setup_sample()

        forest_backend = ForestBackend()
        # This method is supposed to return a dict, whose keys are the string user names of the rewardify users and
        # the values pandas Datetime objects for some time 1701. This is supposed to represent the last tree, the
        # backend has granted gold for.
        state = forest_backend._default_state()

        self.assertIsInstance(state, dict)
        self.assertEqual(len(state), 2)
        self.assertEqual(state['Jonas'].year, 1701)

    def test_load_state_works(self):
        self.setup_sample()

        # Now we also need to create the json file, which contains the state
        date_time = pandas.to_datetime("Mon Dec 10 16:01:22 GMT+01:00 2018")
        state = {
            'Jonas':        str(date_time),
            'Joana':        str(date_time)
        }
        file_path = os.path.join(self.FOLDER_PATH, ForestBackend.STATE_FILE_NAME)
        with open(file_path, mode="w") as file:
            json.dump(state, file)

        self.assertTrue(os.path.exists(file_path))

        forest_backend = ForestBackend()
        self.assertNotEqual(forest_backend.state['Jonas'].year, 1701)

    def test_get_update(self):
        self.setup_sample()

        forest_backend = ForestBackend()
        update_dict = forest_backend.get_update()
        self.assertEqual(len(update_dict), 2)
        self.assertEqual(len(update_dict['Joana']), 7)
        self.assertEqual(len(update_dict['Jonas']), 6)

    # HELPER METHODS
    # --------------

    def setup_sample(self):
        # This method will use a template and the given values to create a new "config.py" file in the testing config
        # folder
        self.create_config(
            self.SAMPLE_IMPORTS,
            self.SAMPLE_DATABASE_DICT,
            self.SAMPLE_BACKEND,
            self.SAMPLE_REWARDS,
            self.SAMPLE_PACKS,
            self.SAMPLE_PLUGIN_CODE
        )

        # This method will create all the CSV files into the testing config folder
        self.create_sample_csv_files()

    def create_sample_csv_files(self):
        for name, content in self.SAMPLE_CSV_FILES.items():
            path = os.path.join(self.FOLDER_PATH, name)
            with open(path, mode='w') as file:
                file.write(content)

    def get_sample_csv_paths(self):
        paths = []
        for name in self.SAMPLE_CSV_FILES.keys():
            path = os.path.join(self.FOLDER_PATH, name)
            paths.append(path)
        return paths
