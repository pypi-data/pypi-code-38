import os
import re
import shutil

import unittest

from py_buildsystem.FilesFinder.FilesFinder import FilesFinder

script_file_path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

test_files_directory_name = "/test_files"

test_files_path = script_file_path + test_files_directory_name

test_files_names = ["test.c", "test.h", "test.o", "test_test.c", "test_test.h", "test_test.o", "test_c_test.c",
                    "test_h_test.h", "test_o_test.o", "testc"]

test_files_in_directories = ["/tes1/test1.c", "/test1/test1.h", "/test1/test1.o", "/tes2/test2.c", "/test2/test2.h", "/test2/test2.o"]


class TestFileFinder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs(test_files_path, exist_ok=True)

        for file in test_files_names:
            with open(os.path.join(test_files_path, file).replace("\\", "/"), "w"):
                pass

        for file in test_files_in_directories:
            os.makedirs(os.path.dirname(test_files_path + file), exist_ok=True)
            with open(test_files_path + file, "w"):
                pass

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(test_files_path, ignore_errors=True)

    def setUp(self):
        self.c_files = []
        self.h_files = []
        self.excludeded_paths = []
        self.regex_test_files = []
        self.test_files_with_path = []
        self.test_files_in_subdirectories_with_path = []
        self.c_test_files_with_path = []

        for file in test_files_names:
            self.test_files_with_path.append(test_files_path + "/" + file)

        for file in test_files_in_directories:
            self.test_files_in_subdirectories_with_path.append(test_files_path + file)

        for file in self.test_files_with_path:
            if file.endswith(".c"):
                self.c_test_files_with_path.append(file)

        self.all_files = self.test_files_with_path + self.test_files_in_subdirectories_with_path

        for file in self.all_files:
            if file.endswith(".c"):
                self.c_files.append(file)

        for file in self.all_files:
            if file.endswith(".h"):
                self.h_files.append(file)

        self.regex = re.compile(".*test_[c|o|h]_test.[c|h|o]")

        for file in self.all_files:
            if self.regex.match(file) is not None:
                self.regex_test_files.append(file)

        for file in self.all_files:
            if not("/test1/" in file or "/test2/" in file):
                self.excludeded_paths.append(file)

    def test_init(self):
        with self.assertRaises(TypeError):
            FilesFinder(1)

        with self.assertRaises(TypeError):
            FilesFinder(" ", 1)

        with self.assertRaises(TypeError):
            FilesFinder([" ", " "], " ", 1)

        with self.assertRaises(TypeError):
            FilesFinder([" ", " "], " ", [" ", " "], 2)

        FilesFinder()

        FilesFinder(" ", " ", None, False)

        FilesFinder(" ", " ", " ", False)
        FilesFinder([" ", " "], " ", " ", False)
        FilesFinder([" ", " "], " ", [" ", " "], False)
        FilesFinder(" ", " ", [" ", " "], False)

    def test_search(self):
        files_finder_path_only = FilesFinder(test_files_path)
        files_finder_regex_test = FilesFinder(test_files_path, ".*\.c$")
        files_finder_regex_test2 = FilesFinder(test_files_path, ".*test_[c|o|h]_test\.[c|h|o]")
        files_finder_exclude_dirs = FilesFinder(test_files_path, list_of_paths_to_exlude_from_search=["/test1/", "/test2/"])
        files_finder_c_files_no_subdirs = FilesFinder(test_files_path, ".*\.c$", search_subdirectories=False)

        self.assertCountEqual(files_finder_path_only.search(), self.all_files)
        self.assertCountEqual(files_finder_regex_test.search(), self.c_files)
        self.assertCountEqual(files_finder_regex_test2.search(), self.regex_test_files)
        self.assertCountEqual(files_finder_c_files_no_subdirs.search(), self.c_test_files_with_path)
        self.assertCountEqual(files_finder_exclude_dirs.search(), self.excludeded_paths)

    def test_set_files_extentions(self):
        files_finder = FilesFinder(test_files_path)

        with self.assertRaises(TypeError):
            files_finder.set_files_extentions(1)

        with self.assertRaises(TypeError):
            files_finder.set_files_extentions([1, 2])

        files_finder.set_files_extentions(".c")
        self.assertCountEqual(files_finder.search(), self.c_files)

        files_finder.set_files_extentions("*.c")
        self.assertCountEqual(files_finder.search(), self.c_files)

        files_finder.set_files_extentions([".c", ".h"])
        self.assertCountEqual(files_finder.search(), self.c_files + self.h_files)

        files_finder.set_files_extentions([".c", "*.h"])
        self.assertCountEqual(files_finder.search(), self.c_files + self.h_files)

        files_finder.set_files_extentions([".g", ".hpp"])
        self.assertCountEqual(files_finder.search(), [])
