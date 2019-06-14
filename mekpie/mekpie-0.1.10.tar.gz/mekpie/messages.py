from .definitions import VERSION

usage = '''
Usage:
    mekpie [options] `command` [command args...] -- [program args...]

Options:
    -h, --help      Display this message
    -V, --version   Print version info and exit
    -q, --quiet     No output to stdout
    -r, --release   Run the command for release
    -m, --mode      Provide a mode
    -c, --changedir Run the mekpie command in the provided directory
    -d, --developer Run mekpie in developer mode

Commands:
    `new`   name     Create a new mekpie project
    `test`  names... Build and execute tests or test
    `clean`          Remove artefacts from previous builds
    `build`          Compile the current project
    `run`            Build and execute main
    `debug`          Build and execute under a debugger
    `dist`           Create an executable in the project root

'''

version = f'''
    mekpie version {VERSION}
'''

no_command = '''
!! Invalid command: No command provided!

    mekpie expects a command following its invocation.
    The following commands are available:

        `help`    Display a help message
        `version` Print version info and exit
        `new`     Create a new mekpie project
        `init`    Create a project in an existing directory
        `test`    Build and execute tests or test
        `clean`   Remove artefacts from previous builds
        `build`   Compile the current project
        `run`     Build and execute main
        `debug`   Build and execute under a debugger
        `dist`    Create an executable in the project root
'''

repeated_option = '!! Repeated option: option {} appears twice!'

too_many_arguments = '!! Unexpected argument: Too many arguments provided!'

unknown_argument = '!! Unexpected argument: Unknown argument provided!'

name_cannot_already_exist = '''
!! Invalid Argument: Cannot create a project in a directory that already exists!

    The directory "./{}" already exists. If you want to use this folder with
    mekpie, navigate within the folder, and run the `init` command.
'''

name_cannot_be_empty = '''
!! Missing argument: You must provide the positional argument `name`!

    When creating a project with `new` or `init` you must provide a positional
    argument `name` after the command.
'''

execution_error = '''
!! Execution error: Error while trying to execute a python resource!
    
    Error occured when attempting to execute: {}

{}
'''

compiler_config_error = '''
!! Config error: Invalid compiler configuration!

    Exptected one of the following: {}
    Instead found a value of: {}
'''

type_error = '''
!! Config error: Invalid type!

    Expected `{}` to be of type: {}
    Instead found a value of type: {}
{}
'''

file_not_found = '''
!! File not found: Could not find "{}"!
'''

directory_not_found = '''
!! Directory not found: Could not find "{}"!
'''

compiler_flag_error = '''
!! Flags not found: Could not find compiler flag for "{}" with purpose "{}"!

    Add the following entry to mek.py to include the correct flag:
    {}
'''

no_tests = '''
!! No tests found: Could not find any tests to run in /tests/!

    Try adding a c source file with a `main` function to /tests/
'''

no_tests_with_name = '''
!! No tests found: Could not find any test with the name {} in /tests/!

     Check that you spelled the test name correctly.
'''

api_no_options = '''
!! No options: API call to mekpie was made without an `Options` instance!

     Call `core.mekpie` with an instance of `definitions.Options`
'''

failed_compiler_call = '''
!! Build failed: the following call to the compiler failed:

    {}

And the following errors were produced:
    {}
'''

failed_program_call = '''
!! Call failed: the following program call failed:

    {}
'''

release_debug = '''
!! Build failed: cannot launch debugger for a release build

    To launch the debugger run the command again without the --release flag.
'''

created = '''
{} created successfully!
'''

initialized = '''
{} initialized successfully!
'''

clean = '''
Project successfully cleaned.
'''

build_succeeded = '''
Project successfully built. ({:.3f}s)
'''

mekpie_config_name = (
    'Please provide a name for your project',
    '{} is not a valid project name!'
)

compiler_configs = '''
Mekpie supports the following c compilers, please select one (compilers must be installed seperately):
    - `gcc_clang`   for use with the gcc or clang compiler 
    - `emscripten`  for use with the emscripten c to js compiler
    - `avr_gcc`     for use with avr-gcc and avrdude
'''

mekpie_config_cc = (
    'Please select a cc',
    '{} is not a valid cc! See the list above.'
)