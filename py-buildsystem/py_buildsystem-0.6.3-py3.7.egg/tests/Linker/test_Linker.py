import os
import time
import shutil
import subprocess

import unittest

from py_buildsystem.Toolchain.Linker.Linker import Linker

script_file_path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

test_linker_dir_name = "test_compier"
test_linker_name = "test_linker"
output_directory = "../output"

test_linker_path = os.path.join(script_file_path, test_linker_dir_name).replace("\\", "/")
test_linker_exe_path = os.path.join(test_linker_path, test_linker_name).replace("\\", "/")

config = {
    "comand_line_file": "@",
    "output_flag": "-o"
}

flags = ["-lgtest"]

files_to_link = ["test1.o", "test2.o", "test3.o", "test4.o", "test5.o", "test6.o"]
output_file = "output"

time_value = 10


class TestLinker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs(test_linker_path, exist_ok=True)

        with open(test_linker_exe_path, "wb") as file:
            pass

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(test_linker_path, ignore_errors=True)

    def test_read_config_file(self):
        pass

    def test_compile_single_file(self):
        subprocess.call = self.subprocess_call_mock_single_file

        orginal = time.time
        time.time = self.time_time_mock

        self.expected_command = [test_linker_exe_path, flags[0], config["comand_line_file"] + str(time_value) + "linker_file", config["output_flag"] + output_file]

        linker = Linker(test_linker_exe_path, config["output_flag"], config["comand_line_file"])
        linker.set_flags(flags)

        linker.link([files_to_link[0]], output_file)

        time.time = orginal

    def test_compile_multiple_files(self):
        subprocess.call = self.subprocess_call_mock_increment_num_of_calls

        self.num_of_calls = 0

        linker = Linker(test_linker_exe_path, config["output_flag"], config["comand_line_file"])

        linker.link(files_to_link, output_directory)

        self.assertEqual(self.num_of_calls, 1)

    def subprocess_call_mock_single_file(self, command):
        self.assertCountEqual(command, self.expected_command)

    def subprocess_call_mock_increment_num_of_calls(self, command):
        self.num_of_calls += 1

    def time_time_mock(self):
        return time_value
