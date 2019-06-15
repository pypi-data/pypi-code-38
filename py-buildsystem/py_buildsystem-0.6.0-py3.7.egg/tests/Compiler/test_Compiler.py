import os
import shutil
import subprocess

import unittest

from py_buildsystem.Toolchain.Compiler.Compiler import Compiler

script_file_path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

test_compiler_dir_name = "test_compier"
test_compiler_name = "test_compiler"
output_directory = "../output"

test_compiler_path = os.path.join(script_file_path, test_compiler_dir_name).replace("\\", "/")
test_compiler_exe_path = os.path.join(test_compiler_path, test_compiler_name).replace("\\", "/")

config = {
    "define_flag": "-D",
    "output_flag": "-o",
    "compile_flag": "-c",
    "include_flag": "-I"
}

flags = ["-std=c++14"]
defines = ["DEBUG", "X86"]
includes = ["../inc", "../../framework/include"]

files_to_compile = ["test1.c", "test2.c", "test3.c", "test4.c", "test5.c", "test6.c"]
output_files = [file.replace(".c", ".o") for file in files_to_compile]


class TestCompiler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs(test_compiler_path, exist_ok=True)

        with open(test_compiler_exe_path, "wb") as file:
            pass

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(test_compiler_path, ignore_errors=True)

    def test_read_config_file(self):
        pass

    def test_compile_single_file(self):
        subprocess.call = self.subprocess_call_mock_single_file

        self.expected_command = [test_compiler_exe_path, config["compile_flag"], config["define_flag"] + defines[0], config["define_flag"] + defines[1],
                                 flags[0], config["include_flag"] + includes[0], config["include_flag"] + includes[1], config["output_flag"] + output_directory + "/" + output_files[0], files_to_compile[0]]

        compiler = Compiler(test_compiler_exe_path, config["define_flag"], config["output_flag"], config["compile_flag"], config["include_flag"])
        compiler.set_defines(defines)
        compiler.set_includes(includes)
        compiler.set_flags(flags)

        compiler.compile([files_to_compile[0]], output_directory)

        self.expected_command = [test_compiler_exe_path, config["compile_flag"], config["define_flag"] + defines[0],
                                 config["include_flag"] + includes[0], config["output_flag"] + output_directory + "/" + output_files[1], files_to_compile[1]]

        compiler = Compiler(test_compiler_exe_path, config["define_flag"], config["output_flag"], config["compile_flag"], config["include_flag"])
        compiler.set_defines([defines[0]])
        compiler.set_includes([includes[0]])

        compiler.compile([files_to_compile[1]], output_directory)

    def test_compile_multiple_files(self):
        subprocess.call = self.subprocess_call_mock_increment_num_of_calls

        self.num_of_calls = 0

        compiler = Compiler(test_compiler_exe_path, config["define_flag"], config["output_flag"], config["compile_flag"], config["include_flag"])

        compiler.compile(files_to_compile, output_directory)

        self.assertEqual(self.num_of_calls, len(files_to_compile))

        self.num_of_calls = 0

        compiler = Compiler(test_compiler_exe_path, config["define_flag"], config["output_flag"], config["compile_flag"], config["include_flag"])

        compiler.compile(files_to_compile[2:], output_directory)

        self.assertEqual(self.num_of_calls, len(files_to_compile[2:]))

    def subprocess_call_mock_single_file(self, command):
        self.assertCountEqual(command, self.expected_command)

    def subprocess_call_mock_increment_num_of_calls(self, command):
        self.num_of_calls += 1
