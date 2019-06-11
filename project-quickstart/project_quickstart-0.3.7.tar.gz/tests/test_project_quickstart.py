'''
test_project_quickstart.py
================

:Author: |author_names|
:Release: |version|
:Date: |today|


Purpose
=======

Run tests for project_quickstart

project_quickstart tests:

# Workflow:
  # run flake8 for each file (within vim and in root dir)
  # Use pytest only, test locally, then upload for CI

# For each dir generate and compare directory trees and compare ref and test files
# For each script (py and R) compare ref and test files
# Leave contents for manual diff if test fails


Usage and options
=================

Usage:
       pytest test_project_quickstart.py
       test_project_quickstart.py [-h | --help]

Options:
    -h --help           Show this screen

'''
##############
# Get all the modules needed
# System:
import pytest
import os
import tempfile

# Import helper functions from this package:
import pytest_helpers
##############


##############
# Tests for project_quickstart

#####
# Set up options to run:
test_name = 'pq_test_ref'

# For each dir generate and compare directory trees and compare ref and test files
# For each script (py and R) compare ref and test files
cli_options = [['project_quickstart', '-n', '{}'.format(test_name)],
               ['project_quickstart', '--script-python={}'.format(test_name)],
               ['project_quickstart', '--script-R={}'.format(test_name)],
               ['project_quickstart', '--script-pipeline={}'.format(test_name)],
               ['project_quickstart', '--example'],
               ]

dirs = ['{}'.format(test_name),
        'pipeline_{}'.format(test_name),
        'pq_example',  # this is fixed for --example
        ]

# Not tested:
# project_quickstart --help
# project_quickstart --version

# Not in use:
# project_quickstart --force
# project_quickstart --dry-run


# Get directory for reference files:
ref_dir = os.path.abspath(os.path.join('tests', 'ref_files'))
print(ref_dir)

# Create temporary directory for test outputs:
test_dir = tempfile.mkdtemp()
print(test_dir)
os.chdir(test_dir)
#####


#####
# Generate test sets
# Run each project_quickstart CLI option:
# Functions that are needed to create test files should use the pytest.fixture decorator
@pytest.fixture
def run_cmds():
    '''
    Run command line options for project_quickstart
    '''
    pytest_helpers.run_CLI_options(cli_options)


# For each dir generate and compare directory tree files:
@pytest.fixture
def dir_trees():
    '''
    Generate files with the directory trees for project_quickstart
    '''
    pytest_helpers.create_dir_tree(dirs, '.tree')


# Collect and compare directory tree files (should all end in eg '.tree'):
# Tree dir files prob get collected and compared twice
# pytest only picks files AND functions starting with 'test_'
# def test_collect_and_compare_trees(run_cmds, dir_trees):
    # ref_tree = pytest_helpers.collect_files(ref_dir, '.tree')
    # test_tree = pytest_helpers.collect_files(test_dir, '.tree')
    # pytest_helpers.compare_all_files(ref_tree, test_tree)


# Collect and compare for each dir from ref and test, this will include files
# created with '--script-' options and files with tree dirs:
def test_collect_and_compare_all_files(run_cmds, dir_trees):
    '''
    Run project_quickstart commands and files with directory tree for this test and
    compare outputs of test vs reference files. Checks number of files, names of files
    and content of each test vs ref pair.
    '''
    dirs.append('.')  # Add cwd after creating tree dirs else erros as different lengths
    pytest_helpers.compare_ref_and_test_dirs(dirs, ref_dir, test_dir, suffix = '')


print('Tests finished')
#####
##############
