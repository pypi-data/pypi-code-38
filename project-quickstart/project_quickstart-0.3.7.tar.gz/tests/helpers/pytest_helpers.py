'''
pytest_helper_funcs.py
=======================

:Author: |author_names|
:Release: |version|
:Date: |today|


Purpose
=======

Helper functions for tests for project_quickstart

Import as a module

A file conftest.py needs to exist containing:
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

for pytest to import this file as a module.

'''
##############
# Get all the modules needed
# System:
import os
import hashlib
import subprocess
import sys
import difflib
##############


##############
# Helper functions
# Run each project_quickstart CLI option:
def run_CLI_options(options):
    '''
    Execute each command-line option. Pass options as a list of strings,
    each being a command with arguments for the CLI package to test.
    If the process fails it is communicated (check = True with output captured).
    '''
    for option in options:
        print('\n', 'Test message: ', 'Executing command: ', ' '.join(option))
        subprocess.run(option, check = True)

    return


# Get trees for each directory:
def create_dir_tree(dirs, suffix):
    '''
    For a given directory d create a tree directory using
    ls -Ra1 d > d.suffix
    '''
    print('\n', 'Test message: ', 'Creating trees of directories from: {}'.format(dirs),)
    for d in dirs:
        # ls in OS X doesn't seem to print first folder grouping, Ubuntu does
        # ref vs test files will fail in travis, use python file lists only
        # name = str(str(d) + suffix)
        # print('Test message: ', 'Creating tree directory: {}'.format(name),)
        # The following doesn't work with pipes
        # Also note that shell = True changes how the first arguments are interpreted
        # See:
        # https://medium.com/python-pandemonium/a-trap-of-shell-true-in-the-subprocess-module-6db7fc66cdfd
        # cmd = ['ls', '-Ra1', str(d), str('>'), str(name)]
        # cmd = 'ls -Ra1 {} > {}'.format(str(d), str(name))
        # print(cmd)
        # subprocess.run(cmd, check = True, shell = True)
        # Note security issues with shell = True, should instead do eg:
        # https://stackoverflow.com/questions/24306205/file-not-found-error-when-launching-a-subprocess-containing-piped-commands
        # https://stackoverflow.com/questions/13332268/python-subprocess-command-with-pipe
        # https://docs.python.org/3/library/subprocess.html#subprocess.run

        # Use python instead to avoid system problems:
        for d in dirs:
            name = str(str(d) + '.py_tree')
            name = open(name, 'w')
            d_list = []
            for dirpath, dirnames, filenames in os.walk(d):
                for f in filenames:
                    d_list.append(f)
            d_list.sort()
            name.write('\n'.join(d_list))
            name.close()

    return


# Collect files with tree directories:
def collect_files(dir_to_search, suffix):
    '''
    Collect files to compare from a named directory and ending with a given suffix
    '''
    # Collect files:
    file_list = []
    dir_to_search = os.path.abspath(dir_to_search)

    for dirpath, dirnames, filenames in os.walk(dir_to_search):
        for d in dirnames:
            for f in filenames:
                f = os.path.join(dirpath, f)
                if f.endswith(suffix) and f not in file_list:
                    file_list.append(f)

    print('\n', 'Test message: ', 'Collecting files from directories')
    print('Test message: ', 'Directory: {}'.format(dir_to_search))
    print('contains: ', file_list)

    return(file_list)


# Function to compare text files:
def compare_files(ref, test):
    '''
    Compare text files line by line, outputs lines which differ.
    '''
    print('\n', 'Test message: ', 'Comparing individual files')
    print('Test message: ', 'ref file is: ', ref)
    print('Test message: ', 'test file is: ', test)

    # Read each file:
    ref1 = open(ref, 'r')
    test1 = open(test, 'r')
    ref_read = ref1.read()
    test_read = test1.read()

    if ref_read != test_read:
        print('''\n,
                 Test message: Files are not the same, compared:
                 {}
                 and
                 {}
              '''.format(ref, test)
              )
        # Compare line by line and output differences
        # Files were read already so close and read again
        # Files should be small, must be a better way though
        ref1.close()
        test1.close()

        print('Test message: ', 'Comparing line by line:', '\n')
        # Re-open for readlines():
        ref = open(ref, 'r')
        test = open(test, 'r')
        diff = difflib.unified_diff(ref.read(),  # ref.readlines(),
                                    test.read(),  # test.readlines(),
                                    fromfile = 'ref',
                                    tofile = 'test'
                                    # lineterm = '\n'
                                    )

        # TO DO: Print first lines only
        # counter = 0
        # while counter < 21:
            # print(counter)
        for line in diff:
            # counter += 1
            sys.stdout.write(line)

        # Clean up:
        print('\n', 'Test message: ', 'End of file comparison')
        ref.close()
        test.close()
        sys.exit('Test message: Exiting now...')

    else:
        print('Test message: ', 'Files are the same')
        assert ref_read == test_read
        ref1.close()
        test1.close()

    return


# Compare two sets of text files:
def compare_all_files(ref_list, test_list):
    '''
    Compare files between ref_list and test_list
    '''
    # Sort lists to ensure order:
    ref_list.sort()  # in place
    test_list.sort()  # in place
    print('\n', 'Test message: ', 'Comparing files between two sets of files')
    print('\n', 'ref list is: ', ref_list)
    print('\n', 'test list is: ', test_list)

    # Check length is the same and not 0:
    assert len(ref_list) > 0
    assert len(test_list) > 0
    assert len(ref_list) == len(test_list)
    print('\n', 'Test message: ', 'Lengths of ref list and test list are the same')

    # Contents should be the same and in the same order:
    for ref, test in zip(ref_list, test_list):
        ref_base = os.path.basename(ref)
        test_base = os.path.basename(test)
        print('ref base is: ', ref_base)
        print('test base is: ', test_base)
        assert str(ref_base) == str(test_base)
    print('Test message: ', 'ref list and test list contain the same elements')

    # Compare files:
    for ref, test in zip(ref_list, test_list):
        compare_files(ref, test)

    return


# Collect and compare files using functions above:
def compare_ref_and_test_dirs(dirs, ref_dir, test_dir, suffix):
    '''
    For each directory specified in list dirs, generate and compare ref and test files.
    Use collect_files(dir, suffix) and compare_all_files(ref_list, test_list) functions.
    '''
    print('\n', 'Comparing contents of files for each directory')
    print('Directories provided: {}'.format(dirs))
    for d in dirs:
        d_ref = os.path.abspath(os.path.join(ref_dir, d))
        d_test = os.path.abspath(os.path.join(test_dir, d))
        print('\n', 'ref dir: ', d_ref)
        print('test dir: ', d_test)
        ref_files = collect_files(d_ref, suffix)
        test_files = collect_files(d_test, suffix)

        # Run compare_all_files() for tree directory files:
        compare_all_files(ref_list = ref_files, test_list = test_files)

    return


# Compute md5sums for each file created from each CLI option run:
def compute_checksum(filename):
    '''
    Return md5 checksum
    '''
    md5 = hashlib.md5(open(filename, 'rb').read()).hexdigest()

    return(md5)
##############
