from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()
import subprocess
import os
import inspect
import sys


def get_package_root():
    from . import __file__ as initpy_file_path
    return os.path.dirname(initpy_file_path)


base_dir = get_package_root()
logo_path = os.path.join(base_dir, "resources", "typhoonelephant.jpg")


def pytest_addoption(parser):
    parser.getgroup("reporting").addoption("--allure-docx",
                                           action="store_true",
                                           help="Create a docx file from allure results")

    parser.getgroup("reporting").addoption("--allure-docx-pdf",
                                           action="store_true",
                                           help="Create a docx file from allure results and generate a pdf")

    parser.getgroup("reporting").addoption("--allure-docx-title",
                                           default="TyphoonTest",
                                           help="Custom title for docx reports")

    parser.getgroup("reporting").addoption("--allure-docx-logo",
                                           default=logo_path,
                                           help="Path to custom logo image for the docx report")

    parser.getgroup("reporting").addoption("--allure-docx-logo-height",
                                           default=3,
                                           help="Height of custom logo in centimeters. Width is adjusted to keep aspect ratio")


_pytest_config = None


def pytest_configure(config):
    global _pytest_config
    _pytest_config = config


def pytest_unconfigure():
    report_dir = _pytest_config.option.allure_report_dir
    allure_docx = _pytest_config.option.allure_docx
    allure_pdf = _pytest_config.option.allure_docx_pdf

    allure_docx_title = _pytest_config.option.allure_docx_title
    allure_docx_logo = _pytest_config.option.allure_docx_logo
    allure_docx_logo_height = _pytest_config.option.allure_docx_logo_height

    if report_dir is not None:
        if allure_docx or allure_pdf:
            options = ["--title={}".format(allure_docx_title),
                       "--logo={}".format(allure_docx_logo),
                       "--logo-height={}".format(allure_docx_logo_height),
                       ]
            if allure_pdf:
                options.append("--pdf")
            options = " ".join(options)

            dir_name = os.path.basename(os.path.normpath(report_dir))
            output_file = dir_name+".docx"

            cmd_name = "{}_generate_docx.cmd".format(dir_name)
            with open(cmd_name,'w') as file:
                file.write("@echo off\n")
                file.write("echo Generating TyphoonTest DOCX/PDF report\n")
                file.write("allure-docx {} {} {}".format(options, report_dir, output_file))
                file.write(" && echo Finished without errors.")
                file.write(" && timeout 2 > NUL && exit")
            # Looks convoluted but:
            # first "cmd" is to avoid using shell=True
            # "start" opens in new window, second "cmd /c" is to make it close automatically
            subprocess.check_output(["cmd", "/c", "start", "cmd", "/k", cmd_name])
