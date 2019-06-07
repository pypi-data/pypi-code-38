# -*- coding: utf-8 -*-

###
# © 2018 The Board of Trustees of the Leland Stanford Junior University
# Nathaniel Watson
# nathankw@stanford.edu
###

# For some useful documentation, see
# https://docs.python.org/2/distutils/setupscript.html.
# This page is useful for dependencies:
# http://python-packaging.readthedocs.io/en/latest/dependencies.html.

# PSF tutorial for packaging up projects:
# https://packaging.python.org/tutorials/packaging-projects/

import glob
import os
from setuptools import setup, find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()

SCRIPTS_DIR = os.path.join("sruns_monitor", "scripts")
scripts = glob.glob(os.path.join(SCRIPTS_DIR,"*.py"))
scripts.remove(os.path.join(SCRIPTS_DIR,"__init__.py"))
scripts.append("sruns_monitor/tests/monitor_integration_tests.py")

setup(
  author = "Nathaniel Watson",
  author_email = "nathan.watson86@gmail.com",
  classifiers = [
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
  ],
  description = "Looks for new Illumina sequencing runs and tars them up into GCP storage",
  entry_points = {
      "console_scripts": [
          "srun-mon=sruns_monitor.scripts.launch_monitor:main"
      ]
  },
  keywords = "archive sequencing runs monitor",
  install_requires = [
    "docutils",
    "google-cloud-firestore",
    "google-cloud-storage",
    "jsonschema",
    "psutil"
  ],
  long_description = long_description,
  long_description_content_type = "text/x-rst",
  name = "sruns-monitor",
  packages = find_packages(),
  package_data = {
      "sruns_monitor": ["schema.json"],
      "sruns_monitor.tests": ["SEQ_RUNS/*/*"]
  },
  project_urls = {
      "Read the Docs": "https://sruns-monitor.readthedocs.io/en/latest"
  },
  scripts = scripts,
  url = "https://pypi.org/project/sruns-monitor/",
  version = "0.5.0"
)
