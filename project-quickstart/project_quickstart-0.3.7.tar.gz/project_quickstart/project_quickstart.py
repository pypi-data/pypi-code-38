'''
project_quickstart - setup a new python based project
=====================================================

:Author: Antonio Berlanga-Taylor
:Release: |version|
:Date: |date|


Purpose
=======

This script creates a python data science project template. The idea is
to be able to easily turn a project into a package with software testing,
version control, reporting, docs, etc.

Once you've quickstarted your project you can run the --script options to
create python and R script templates or a Ruffus/CGAT pipeline template.

You will need to install other software (e.g. R, Ruffus, Sphinx, etc.) to make
full use depending on your preferences.


Usage and Options
=================

Create a new directory, subfolders and files in the current directory that will
help quickstart your data science project with packaging, testing, scripts and
other templates.

Usage:
       project_quickstart [--project-name=<project_name> | -n <project_name>] ...
       project_quickstart [--script-python=<script_name>]
       project_quickstart [--script-R=<script_name>]
       project_quickstart [--script-pipeline=<pipeline_name>]
       project_quickstart [--example]
       project_quickstart [-f | --force]
       project_quickstart [-h | --help]
       project_quickstart [--version]
       project_quickstart [--dry-run]

Options:
    --project-name=DIR -n DIR     Creates a project skeleton
    --script-python=FILE          Create a python script template, '.py' is appended.
    --script-R=FILE               Create an R script template, '.R' is appended.
    --script-pipeline=FILE        Create a Ruffus/CGAT pipeline template,
                                  'pipeline_FILE.py' is created.
    --example                     Create a project_quickstart example with
                                  runnable scripts and pipeline.
    -f --force                    Take care, forces to overwrite files and directories.
    -h --help                     Show this screen.
    --version                     Show version.
    --dry-run                     Print to screen only.

Documentation
=============

  For more information see:

      https://github.com/AntonioJBT/project_quickstart

'''
##############################
# Standard Python modules:
import sys
import os
import shutil

# Modules with Py2 to 3 conflicts:
try:
    import configparser
except ImportError:  # Py2 to Py3
    import ConfigParser as configparser

# Modules not in core library:
import docopt

# Package module:
import project_quickstart.projectQuickstart as projectQuickstart
import project_quickstart.version as version

version = version.set_version()

# Get package source directory in (param path) '
src_dir = projectQuickstart.getDir('..')

# For debugging:
# print('project_quickstart package directory is:', '\n', src_dir)

# Global variable for configuration file ('.ini')
# allow_no_value addition is from:
# https://github.com/docopt/docopt/blob/master/examples/config_file_example.py
# By using `allow_no_value=True` we are allowed to
# write `--force` instead of `--force=true` below.
CONFIG = configparser.ConfigParser(allow_no_value = True)

##############################


##############################
def main():
    ''' with docopt main() expects a dictionary with arguments from docopt()
    docopt will automatically check your docstrings for usage, set -h, etc.
    '''
    options = docopt.docopt(__doc__, version = version)
    welcome_msg = str('\n' + 'Welcome to project_quickstart version {} (!).'
                      + '\n').format(version)
    # print(welcome_msg)
    docopt_error_msg = str('project_quickstart exited due to an error.' + '\n')
    docopt_error_msg = str(docopt_error_msg
                           + '\n'
                           + 'Try project_quickstart --help'
                           + '\n' + '\n'
                           + 'Options in place:'
                           + '\n'
                           + str(options)
                           + '\n'
                           )

    try:
        # Parse arguments, use file docstring as a parameter definition
        # These arguments are optional
        # help and version are handled automatically by docopt if set in
        # options above.
        # Standard options (log, verbose, version, quiet, dry-run, force):
        if options['--dry-run']:
            print('Dry run, only print what folders will be created.')
            print('Option not in use at the moment')
            pass  # TO DO

        if options['--force']:
            print('Force overwriting directories and files')
            print('Option not in use at the moment')
            pass  # TO DO

        # Programme specific options
        # Required:
        if options['--project-name']:
            print(welcome_msg)
            project_name = str(options["--project-name"]).strip('[]').strip("''")
            project_root = str('{}').format(project_name)

            # Set up default paths, directoy and file names:
            project_dir = os.path.join(os.getcwd(), project_root)

            if not os.path.exists(project_dir):
                os.makedirs(project_dir)

            else:
                print(docopt_error_msg)
                print(str('''The directory with the name {} already exists.
                             Use --force to overwrite.'''
                          + '\n'
                          ).format(project_root)
                      )
                sys.exit()

        # Addional/alternative command line options:
        script_template_py = str('template.py')
        script_template_R = str('template.R')

        if options['--script-python'] and len(options['--script-python']) > 0:
            print(welcome_msg)
            print(''' Copying a Python script template into the current working directory. ''')
            # py3.5 formatting:
            script_name = str(options["--script-python"]).strip('[]').strip("''")
            script_name = str('{}.py').format(script_name)

        elif options['--script-python'] and len(options['--script-python']) == 0:
            print(docopt_error_msg)
            print(''' You need to provide a script name. This will be prefixed to ".py" ''')
            sys.exit()

        if options['--script-R'] and len(options['--script-R']) > 0:
            print(welcome_msg)
            print(''' Copying an R script template into the current working directory. ''')
            script_name = str(options["--script-R"]).strip('[]').strip("''")
            script_name = str('{}.R').format(script_name)

        elif options['--script-R'] and len(options['--script-R']) == 0:
            print(docopt_error_msg)
            print(''' You need to provide a script name. This will be prefixed to ".R" ''')
            sys.exit()

        if options['--script-pipeline'] and len(options['--script-pipeline']) > 0:
            print(welcome_msg)
            print(''' Copying a pipeline template into the current working directory.
                    This includes a Ruffus pipeline.py script template,
                    pipeline yml configuration template for parameters,
                    a report directory with a restructuredText template,
                    and sphinx-quickstart modified conf.py and Makefile files.''')
            pipeline_dir_name = str(options["--script-pipeline"]).strip('[]').strip("''")
            pipeline_dir_name = str('pipeline_{}').format(pipeline_dir_name)
            # All files within the directory
            # project_quickstart/templates/script_templates/pipeline
            # plus
            # project_quickstart/templates/script_templates/pipeline_template.py
            # will get copied over in function below.

        elif options['--script-pipeline'] and len(options['--script-pipeline']) == 0:
            print(docopt_error_msg)
            print(''' You need to provide a pipeline name to generate the
                    directory "pipeline_NAME" ''')
            sys.exit()

        # Exit if options not given:
        if (not options['--project-name']
                and not options['--script-R']
                and not options['--script-python']
                and not options['--script-pipeline']
                and not options['--example']):
            print(docopt_error_msg)
            print('Error in  the options given or none supplied.',
                  '\n',
                  'A project name is required.',
                  'Otherwise you need to use',
                  '--script-R, --script-python or --script-pipeline.')
            sys.exit()

    # Handle exceptions:
    except docopt.DocoptExit:
        print(docopt_error_msg)
        raise

    # Get locations of source code
    # os.path.join note: a subsequent argument with an '/' discards anything
    # before it
    # For function to search path see:
    # http://stackoverflow.com/questions/4519127/setuptools-package-data-folder-location
    # MANIFEST.in file instructs the project_quickstart/templates folder to be
    # included in installation

    template_dir = projectQuickstart.getDir('../templates')
    py_package_template = os.path.join(template_dir, 'project_template')
    report_templates = os.path.join(template_dir, 'report_templates')
    script_templates = os.path.join(template_dir, 'script_templates')
    pipeline_templates = os.path.join(script_templates, 'pipeline_template')
    examples_dir = os.path.join(template_dir, 'examples')

    # Modified sphinx-quickstart templates only live in:
    # templates/project_template/docs/
    # but are needed in
    # code/docs, report directory
    # and pipeline directory:
    sphinx_configs = os.path.join(template_dir, 'project_template', 'docs')
    sphinx_files = ['conf.py',
                    'Makefile',
                    'make.bat',
                    'include_links.rst',
                    'index.rst',
                    ]

    def createProject():
        if options['--project-name']:

            dirs_to_use = [template_dir,
                           py_package_template,
                           report_templates,
                           script_templates
                           ]

        # Sanity check:
            for d in dirs_to_use:
                if not os.path.exists(d):
                    print(docopt_error_msg)
                    print(''' The directory:
                               {}
                               does not exist.
                               Are the paths correct? Did the programme install
                               in the right location?
                               'bin' or equivalent dir should be where
                               project_quickstart installed,
                               'templates' and 'project_template' come with this package.
                          '''.format(d))
                    sys.exit()

        # Get the names for the directories to create for the project skeleton:
        manuscript_dir = os.path.join(project_dir, 'documents_and_manuscript')
        code_dir = os.path.join(project_dir, 'code')
        data_dir = os.path.join(project_dir, 'data')
        results_dir = os.path.join(project_dir, 'results')

        dirnames = [manuscript_dir,
                    # code_dir, # leave out as shutil.copytree needs to
                    # create the
                    # shutil root dir, otherwise files are not copied
                    data_dir,
                    results_dir
                    ]

        # Sanity check:
        for d in dirnames:
            if os.path.exists(d):
                print(docopt_error_msg)
                print(''' The directory:
                           {}
                           already exists.
                           To overwrite use --force.
                      '''.format(d))
                sys.exit()

        # If directory paths are OK, continue:
        print(str('Path in use:' + '\n'
                  + template_dir + '\n'
                  # + py_package_template
                  + '\n' + '\n'
                  + 'Creating the project structure for {} in:'.format(project_name)
                  + '\n'
                  + project_dir + '\n')
              )

        # Create directories:
        # TO DO: pass these from ini file
        # Add hardcoded directories first for now:
        dirnames.extend(["{}/raw".format(data_dir)])
        dirnames.extend(["{}/processed".format(data_dir)])
        dirnames.extend(["{}/external".format(data_dir)])

        tree_dir = []
        for d in map(str, dirnames):
            tree_dir = [d for d in list(dirnames)]

            if not os.path.exists(d):
                os.makedirs(d)
            else:
                print(docopt_error_msg)
                print('''The directory {} already exists, use --force to
                        overwrite.'''.format(d))
                sys.exit()

        return(code_dir, manuscript_dir, data_dir, results_dir, tree_dir)

    # Copy files from template directory:
    # TO DO: 'code' dir is hard coded, change to ini parameter later
    # The intention is to use the 'code' dir as a
    # GitHub/packageable directory

    # For shutil.copytree functions, ignore the following files:
    files_to_ignore = ['dir_bash_history',
                       '__pycache__',
                       '*.bak',
                       'dummy*',
                       ]

    def projectTemplate(src, dst):
        '''
        Copy across project template files for
        a Python/GitHub/etc setup.
        Files {} are ignored.
        '''.format(files_to_ignore)

        if os.path.exists(dst) and not options['--force']:
            print(docopt_error_msg)
            raise OSError('''
                          Directory {} already exists - not overwriting.
                          see --help or use --force
                          to overwrite.
                          '''.format(dst)
                          )
            sys.exit()
        else:
            shutil.copytree(src,
                            dst,
                            ignore = shutil.ignore_patterns(*files_to_ignore)
                            )

    # Copy across individual files outside of the 'templates' dir:
    def copySingleFiles(src, dst, *args):
        '''
        Copies named files into the current working directory
        from a given directory excluding
        {}
        '''.format(files_to_ignore)

        files = []
        for f in os.listdir(src):
            for arg in args:
                if arg in f:
                    files.extend([f])
                else:
                    pass

        for f in map(str, files):
            shutil.copy2(os.path.join(src, f),
                         dst
                         )

    # Replace all instances of template with 'name' from project_name as
    # specified in options:
    def renameTree(full_path, old_substring, new_substring):
        '''
        Rename 'template' and 'project_template' strings to name given for new
        project.
        '''
        for dirpath, dirname, filename in os.walk(full_path):
            for d in dirname:
                for f in os.listdir(os.path.join(dirpath, d)):
                    d = os.path.join(dirpath, d)
                    if old_substring in f:
                        os.rename(os.path.join(d, f),
                                  os.path.join(d, f.replace(old_substring,
                                               '{}').format(new_substring))
                                  )

            for d in dirname:
                if old_substring in d:
                    os.rename(os.path.join(str(dirpath), d),
                              os.path.join(str(dirpath), d.replace(
                                  old_substring, '{}').format(new_substring))
                              )
            # Files in the root dir called don't get renamed, run here:
            for f in os.listdir(dirpath):
                if old_substring in f:
                    os.rename(os.path.join(dirpath, f),
                              os.path.join(dirpath, f.replace(old_substring,
                                           '{}').format(new_substring))
                              )

    # Make single copies of script templates as standalone function:
    def scriptTemplate():
        ''' Copy script templates and rename them according to option given.
            For pipeline option this creates a directory
            with a Ruffus pipeline script template, yml/ini parameters
            file and sphinx-quickstart modified templates.
        '''
        cwd = os.getcwd()

        if options['--script-python']:
            copy_to = os.path.join(cwd, script_name)
            if os.path.exists(copy_to) and not options['--force']:
                print(docopt_error_msg)
                raise OSError(''' File {} already exists - not overwriting,
                              see --help or use --force to overwrite.
                              '''.format(script_name)
                              )
            else:
                copy_from = os.path.join(script_templates, script_template_py)
                shutil.copy2(copy_from, copy_to)
                print(copy_to)

        elif options['--script-R']:
            copy_to = os.path.join(cwd, script_name)
            if os.path.exists(copy_to) and not options['--force']:
                print(docopt_error_msg)
                raise OSError(''' File {} already exists - not overwriting,
                              see --help or use --force to overwrite.
                              '''.format(script_name)
                              )
            else:
                copy_from = os.path.join(script_templates, script_template_R)
                shutil.copy2(copy_from, copy_to)
                print(copy_to)

        elif options['--script-pipeline']:
            copy_to = os.path.join(cwd, pipeline_dir_name)
            if os.path.exists(copy_to) and not options['--force']:
                print(docopt_error_msg)
                raise OSError(''' A directory with the name given
                                  {}
                                  already exists - not overwriting,
                                  see --help or use --force to overwrite.
                              '''.format(copy_to)
                              )
            else:
                shutil.copytree(pipeline_templates,
                                copy_to,
                                ignore = shutil.ignore_patterns(*files_to_ignore)
                                )
                # Report files are now kept in 'pipeline_report', which gets
                # copied across from pipeline.py (as in CGAT pipelines) on
                # execution (so here create skeleton copy)
                # Copy pipeline.yml across:
                copySingleFiles(sphinx_configs,
                                os.path.join(copy_to, 'configuration'),
                                'pipeline.yml')
                # Copy pipeline_report files across:
                copySingleFiles(sphinx_configs,
                                os.path.join(copy_to, 'pipeline_report'),
                                *sphinx_files)
                # Rename all 'template' substrings:
                pipeline_name = str(pipeline_dir_name).strip('pipeline_')
                renameTree(copy_to,
                           'template',
                           pipeline_name
                           )
                print('Created in:', '\n',
                      copy_to)

        else:
            print(docopt_error_msg)
            raise ValueError(''' Bad arguments/options used for script template,
                    try --help''')

    # Call functions according to option given:
    if options['--project-name']:
        # Create the skeleton:
        code_dir, manuscript_dir, data_dir, results_dir, tree_dir = createProject()
        # Copy the code packaging structure and templates:
        projectTemplate(py_package_template, code_dir)
        # Copy script templates to code/project_XXXX/project_XXXX/ :
        copySingleFiles(script_templates,
                        os.path.join(code_dir, 'project_template'),
                        r'.py', r'.R')
                        # code_dir + 'project_template'
                        # will become the user's
                        # new_project/code/new_project directory
                        # where scripts can go in
        # Copy a first pipeline directory with templates on project creation
        # This will have the project name
        # Pipelines created with --script-pipeline are given a different
        # name held
        # in pipeline_dir_name:
        shutil.copytree(pipeline_templates,
                        os.path.join(code_dir,
                                     'project_template',
                                     'pipeline_template'),
                        ignore = shutil.ignore_patterns(*files_to_ignore)
                        )
        # Copy sphinx templates to pipeline_report skeleton directory:
        copySingleFiles(sphinx_configs,
                        os.path.join(code_dir,
                                     'project_template',
                                     'pipeline_template',
                                     'pipeline_report'),
                        *sphinx_files)
        # Copy pipeline yml file to configuration skeleton directory:
        copySingleFiles(sphinx_configs,
                        os.path.join(code_dir,
                                     'project_template',
                                     'pipeline_template',
                                     'configuration'),
                        'pipeline.yml')
        # Copy the report templates to the manuscript directory:
        copySingleFiles(report_templates, manuscript_dir, r'rst')
        # Copy sphinx templates to this manuscript directory:
        copySingleFiles(sphinx_configs,
                        manuscript_dir,
                        *sphinx_files)
        # Add any additional files, like rsync command example:
        copySingleFiles(template_dir, project_dir, r'rsync')
        copySingleFiles(template_dir, project_dir, r'TO_DO')
        copySingleFiles(data_dir, project_dir, r'README_data')
        # Rename 'template' with the project name given:
        renameTree(project_dir, 'project_template', project_name)
        renameTree(project_dir, 'template', project_name)

    # Create a script template copy
    # R and py templates are single, standalone files that get renamed on the
    # go. --script-pipeline copies a directory with script, Sphinx,
    # yml/ini and rst
    # files which get renamed in function above.
    if (options['--script-python']
            or options['--script-R']
            or options['--script-pipeline']
            and not options['--project-name']):
        scriptTemplate()

    # Print a nice welcome message (if successful):
    if options['--project-name']:
        end_msg = str('\n' + """ Done, welcome to {0}!

        Folders and files have been copied to:
        {1}

        The basic structure is:
                              .
                              |-- code
                              |-- data
                              |-- documents_and_manuscript
                              |-- results

        Remember to back up code, data and manuscript directories (or your equivalents).

        The directory:
        {2}

        can be uploaded to a version control system (file templates are for GitHub).
        You could link it to Travis CI, Zenodo and ReadtheDocs for example.
        There are some notes and reminders within the files copied over.
        You may want to change the name 'code' to something more suitable
        when uploading, freezing, packaging, etc.

        Script templates are in:
        {2}/{0}

        The structure largely follows Python packaging conventions.
        You can put scripts, modules and pipelines (eg Ruffus/CGAT, make and
        Makefiles, etc.) in here.

        You can work and save results in:
        {5}

        Install Sphinx to render your rst documents in:
        {3}

        Basic rst template files have been generated already.
        Install and use sphinx-quickstart if you want a more complete skeleton.

        Feel free to raise issues, fork or contribute at:

        https://github.com/AntonioJBT/project_quickstart

        Have fun!

        """.format(project_root,
                   project_dir,
                   code_dir,
                   manuscript_dir,
                   data_dir,
                   results_dir
                   )
        )

        print(end_msg)

    # Finally, last options to run if specified:
    if options['--example'] and not options['--project-name']:
        os.system('project_quickstart -n pq_example')
        os.system('rm -rf pq_example/code/pq_example')
        shutil.copytree(examples_dir,
                        os.path.abspath('pq_example/code/pq_example'),
                        ignore = shutil.ignore_patterns(*files_to_ignore)
                        )

    return


if __name__ == '__main__':
    # if using docopt:
    # it will check all arguments pass, if not exits with 'Usage
    # if arguments are valid, run the program:
    sys.exit(main())
