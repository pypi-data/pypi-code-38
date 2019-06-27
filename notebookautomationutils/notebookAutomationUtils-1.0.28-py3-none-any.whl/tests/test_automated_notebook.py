import os
import unittest
import main.automated_notebook as notebook
from unittest.mock import patch, Mock
from unittest import TestCase

class TestAutomatedNotebook(TestCase):
    """
    Tests for automated notebook
    """
    def test_create_notebook(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath1 = filepath[:index]
        dirpath2 = dirpath1 + "/"

        notebook.create_notebook(dirpath2, 
                         "iOS"
                         "iPhone 7", 
                         "iOS 11.3", 
                         "08/25/2018", 
                         "08/30/2018", 
                         "https://rink.hockeyapp.net/manage/apps/31029/app_versions/7432", 
                         "https://rink.hockeyapp.net/manage/apps/31029/app_versions/7359", 
                         "216",
                         "214",
                         dirpath1)
        expected = dirpath2 + "/Notebook.ipynb"
        assert os.path.exists(expected) == True

    def test_create_notebook_wrong_path(self):
        dirpath = "/abc"

        notebook.create_notebook(dirpath, 
                         "Android"
                         "iPhone 7", 
                         "iOS 11.3", 
                         "08/25/2018", 
                         "08/30/2018", 
                         "https://rink.hockeyapp.net/manage/apps/31029/app_versions/7432", 
                         "https://rink.hockeyapp.net/manage/apps/31029/app_versions/7359", 
                         "216",
                         "214",
                         dirpath)
        expected = dirpath + "/Notebook.ipynb"
        assert os.path.exists(expected) == False
    
    def test_create_notebook_path_is_file(self):
        filepath = os.path.realpath(__file__)

        notebook.create_notebook(filepath, 
                         "iOS"
                         "iPhone 7", 
                         "iOS 11.3", 
                         "08/25/2018", 
                         "08/30/2018", 
                         "https://rink.hockeyapp.net/manage/apps/31029/app_versions/7432", 
                         "https://rink.hockeyapp.net/manage/apps/31029/app_versions/7359", 
                         "216",
                         "214",
                         filepath)
        expected = filepath + "/Notebook.ipynb"
        assert os.path.exists(expected) == False