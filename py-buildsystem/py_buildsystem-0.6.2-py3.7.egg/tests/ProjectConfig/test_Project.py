import os
import yaml
import shutil

import unittest
from unittest.mock import Mock

from py_buildsystem.Project.Project import Project

script_file_path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")

test_files_dir_name = "test_files"

test_config_file_name = "test_project.yaml"
minimal_test_config_file_name = "minimal_test_project.yaml"

test_files_path = os.path.join(script_file_path, test_files_dir_name).replace("\\", "/")

test_config_file_with_path = os.path.join(test_files_path, test_config_file_name).replace("\\", "/")
test_config_file_no_includes_no_defines_with_path = os.path.join(test_files_path, minimal_test_config_file_name).replace("\\", "/")

project_test_configuration = {
    "defines": ["DEBUG"],

    "includes": [
        "test/inc",
        "test1/inc"
    ],

    "steps": [
        {
            "compile First": None,
            "source_directories": ["../../MCU"],
            "output_direcotry": "../../Output/Obj/MCU",
            "types": [".c", ".s"]
        },
        {
            "link Second": None,
            "source_directories": ["../../Output/Obj"],
            "output_file": "../../Output/file.elf",
            "types": [".o"]
        }
    ]
}

empty_project_config = {}


class TestProjectConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs(test_files_path, exist_ok=True)

        with open(test_config_file_with_path, "w") as test_file:
            yaml.dump(project_test_configuration, test_file, indent=2)

        with open(test_config_file_no_includes_no_defines_with_path, "w") as test_file:
            yaml.dump(empty_project_config, test_file, indent=2)

        cls.test_project_name = test_config_file_name.split(".")[0]
        cls.minimal_project_name = minimal_test_config_file_name.split(".")[0]

        cls.toolchain = Mock()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(test_files_path, ignore_errors=True)

    def test_read_config_file(self):
        Project(test_config_file_with_path, self.toolchain)
        Project(test_config_file_no_includes_no_defines_with_path, self.toolchain)

    def test_get_project_name(self):
        project = Project(test_config_file_with_path, self.toolchain)
        empty_project = Project(test_config_file_no_includes_no_defines_with_path, self.toolchain)

        self.assertEqual(project.get_project_name(), self.test_project_name)
        self.assertEqual(empty_project.get_project_name(), self.minimal_project_name)

    def test_get_defines(self):
        project = Project(test_config_file_with_path, self.toolchain)
        empty_project = Project(test_config_file_no_includes_no_defines_with_path, self.toolchain)

        self.assertEqual(project.get_defines(), project_test_configuration["defines"])
        self.assertEqual(empty_project.get_defines(), [])

    def test_get_includes(self):
        project = Project(test_config_file_with_path, self.toolchain)
        empty_project = Project(test_config_file_no_includes_no_defines_with_path, self.toolchain)

        self.assertEqual(project.get_includes(), project_test_configuration["includes"])
        self.assertEqual(empty_project.get_includes(), [])
