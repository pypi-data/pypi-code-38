
import unittest
import configparser

import json
from base.settings import Settings

#data

test_case_data=[
    {"testname":"test_configvalues","section":"chrome","key":"Name","value":"chromedriver.exe"},
    {"testname":"test_configvalues","section":"webbrowser","key":"opacity_threshold","value":0.5},
    {"testname":"test_configvalues","section":"global","key":"temp_processing_folder","value":"E:\\Adhril\\Repo\\FINAPI_by_ML\\temp_processing_folder"},
    {"testname":"test_configvalues","section":"logging","key":"level","value":"DEBUG"},
    {"testname":"test_configvalues","section":"sections_detection_from_joblist_page","key":"trained_model_filename","value":"frozen_inference_graph.pb"},
    {"testname":"test_configvalues","section":"next_button_detection_from_pagination","key":"labelmap_file_filename","value":"labelmap.pbtxt"},
    {"testname":"test_singleton","section":"None","key":"None","value":"None"}
]



class Unit_test_of_settings_class(unittest.TestCase):
    """
        This class contain Test cases for base.settings.Settings class.
        Features of this class:
            - This is implemented 'Singleton' design pattern.
            - Also loads config automatically based on Platform (i.e. linux or windows).

        ** Note : For now, We are tesing this code in Windows Environment.
    """

    def __init__(self,testName,section,key,value):
        super(Unit_test_of_settings_class,self).__init__(testName)
        self.test_section=section
        self.test_key=key
        self.test_value=value
        self.settings_obj=None

    def setUp(self):
        jsonfile_data=open("config"+"\\configWindowsDev.json").read()
        configWindowsDevObj = json.loads(jsonfile_data)
        
        

    def test_singleton(self):
        settings_obj1=Settings()
        settings_obj2=Settings()
        self.assertEqual(id(settings_obj1),id(settings_obj2),"Sigleton unittesting")

    def test_configvalues(self):
        settings_obj1=Settings()
        test_assert_data=None
        if self.test_section=="chrome" and self.test_key=="Name":
            test_assert_data=settings_obj1.get_chrome_Name()
        elif self.test_section=="webbrowser" and self.test_key=="opacity_threshold":
            test_assert_data=settings_obj1.get_webbrowser_opacity_threshold()
        elif self.test_section=="global" and self.test_key=="temp_processing_folder":
            test_assert_data=settings_obj1.get_global_temp_processing_folder()
        elif self.test_section=="logging" and self.test_key=="level":
            test_assert_data=settings_obj1.get_logging_level()
        elif self.test_section=="sections_detection_from_joblist_page" and self.test_key=="trained_model_filename":
            test_assert_data=settings_obj1.get_sections_detection_trained_model_filename()
        elif self.test_section=="next_button_detection_from_pagination" and self.test_key=="labelmap_file_filename":
            test_assert_data=settings_obj1.get_next_button_detection_labelmap_file_filename()
        else:
            print("wrong input")
            
        self.assertEqual( self.test_value,test_assert_data)
            



def suite():
    suite = unittest.TestSuite()
    for test_data in test_case_data:
        testName=test_data["testname"]
        section=test_data["section"]
        key=test_data["key"]
        value=test_data["value"]
        suite.addTest(Unit_test_of_settings_class(testName,section,key,value))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

    # Tested on 2019-05-Feb . Ran succesfully.
