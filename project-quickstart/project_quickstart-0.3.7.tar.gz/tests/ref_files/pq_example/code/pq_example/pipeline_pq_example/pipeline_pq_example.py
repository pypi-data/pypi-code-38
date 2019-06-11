##!/usr/bin/env python3
'''
pipeline_pq_example.py
======================

:Author: |author_name|
:Release: |version|
:Date: |today|


Overview
========

|long_description|


Purpose
=======

This is an example Python pipeline for project_quickstart


Usage and options
=================

These are based on CGATPipelines_ and Ruffus_

.. _CGATPipelines: https://github.com/CGATOxford/CGATPipelines

.. _Ruffus: http://www.ruffus.org.uk/


For command line help type:

    python xxxx/pq_example/code/pq_example/pipeline_pq_example/pipeline_pq_example.py --help


Configuration
=============

This pipeline is built using a Ruffus/CGAT approach. You need to have Python,
Ruffus, CGAT core tools and any other specific dependencies needed for this
script.

A configuration file was created at the same time as this script.

Use this to extract any arbitrary parameters that could be changed in future
re-runs of the pipeline.


Input files
===========

No input is needed, a script generates a tab separated dataframe with simulated
values.


Pipeline output
===============

 Runs python and R scripts from project_quickstart as examples of a
 pipeline with Ruffus and CGAT tools.
A dataframe, several plots and a multi-panel plot are generated.


Requirements
============

CGATPipelines core setup, Ruffus as well as the following
software to be in the path:

Requirements:

See Dockerfile_pq for instructions and dependencies

* R >= 3
* Python >= 3.5
* R data.table
* R stargazer
* R ggplot2
* cgatcore


Documentation
=============

    For more information see:

        |url|

'''
################
# Get modules needed:
import sys
import os
import pprint
import re
import subprocess

# Pipeline:
from ruffus import *

# Database:
import sqlite3

# Try getting CGAT:
try:
    from cgatcore import iotools as iotools
    from cgatcore import pipeline as P
    from cgatcore import experiment as E

except ImportError:
    print('\n', "Warning: Couldn't import CGAT modules, these are required. Exiting...")
    raise

# required to make iteritems python2 and python3 compatible
from builtins import dict

# Import this project's module, uncomment if building something more elaborate: 
#try: 
#    import module_template.py 

#except ImportError: 
#    print("Could not import this project's module, exiting") 
#    raise 

# Import additional packages: 

# Set path if necessary:
#os.system('''export PATH="~/Documents/github.dir/AntonioJBT/project_quickstart/templates:$PATH"''')
################


################

################
# Load options from the config file
# Pipeline configuration
ini_paths = [os.path.abspath(os.path.dirname(sys.argv[0])),
             "../",
             os.getcwd(),
             ]

def getParamsFiles(paths = ini_paths):
    '''
    Search for python ini files in given paths, append files with full
    paths for P.getParameters() to read.
    Current paths given are:
    where this code is executing, one up, current directory
    '''
    p_params_files = []
    for path in ini_paths:
        for f in os.listdir(os.path.abspath(path)):
            ini_file = re.search(r'pipelin(.*).yml', f)
            if ini_file:
                ini_file = os.path.join(os.path.abspath(path), ini_file.group())
                p_params_files.append(ini_file)
    return(p_params_files)

PARAMS = P.get_parameters(getParamsFiles()) # works
#print(PARAMS)
#print(["{}/pipeline.yml".format(os.path.splitext(__file__)[0])])

# Print the options loaded from ini files and possibly a .cgat file:
#pprint.pprint(PARAMS)
# From the command line:
#python ../code/pq_example/pipeline_pq_example/pipeline_pq_example.py printconfig


# Set global parameters here, obtained from the ini file
# e.g. get the cmd tools to run if specified:
#cmd_tools = P.asList(PARAMS["cmd_tools_to_run"])

def get_py_exec():
    '''
    Look for the python executable. This is only in case of running on a Mac
    which needs pythonw for matplotlib for instance.
    '''

    try:
        if str('python') in PARAMS["general"]["py_exec"]:
            print(PARAMS["general"]["py_exec"])
            #py_exec = '{}'.format(PARAMS["general"]["py_exec"])
            py_exec = '%s' % PARAMS["general"]["py_exec"]
    except NameError:
        E.warn('''
               You need to specify the python executable, just "python" or
               "pythonw" is needed. Trying to guess now...
               ''')
    #else:
    #    test_cmd = subprocess.check_output(['which', 'pythonw'])
    #    sys_return = re.search(r'(.*)pythonw', str(test_cmd))
    #    if sys_return:
    #        py_exec = 'pythonw'
    #    else:
    #        py_exec = 'python'
    return(py_exec)
#get_py_exec()

def getINIpaths():
    '''
    Get the path to scripts for this project, e.g.
    project_xxxx/code/project_xxxx/:
    e.g. my_cmd = "%(scripts_dir)s/bam2bam.py" % P.Parameters.get_params()
    '''
    try:
        project_scripts_dir = '{}/'.format(PARAMS['general']['project_scripts_dir'])
        E.info('''
               Location set for the projects scripts is:
               {}
               '''.format(project_scripts_dir)
               )
    except KeyError:
        E.warn('''
               Could not set project scripts location, this needs to be
               specified in the project ini file.
               ''')
        raise

    return(project_scripts_dir)

#print(getINIpaths())
################

################
# Utility functions
def connect():
    '''utility function to connect to database.

    Use this method to connect to the pipeline database.
    Additional databases can be attached here as well.

    Returns an sqlite3 database handle.
    '''

    dbh = sqlite3.connect(PARAMS["database_name"])
    statement = '''ATTACH DATABASE '%s' as annotations''' % (
        PARAMS["annotations"]["database"])
    cc = dbh.cursor()
    cc.execute(statement)
    cc.close()

    return dbh
################

################
def tsvName():
    '''
    Setup the name of the initial tsv dataframe
    '''
    if "pipeline_tsv_example" in PARAMS:
        #tsv_example = P.asList(PARAMS["pipeline_tsv_example"])
        tsv_example = PARAMS["pipeline"]["tsv_example"]
    else:
        tsv_example = 'pandas_df'

    return(tsv_example) # Return as a list, if several names are passed then
                          # several files will be created

tsv_example = tsvName()

# Make sure the python executable and project scripts dir are set:
@follows(get_py_exec, getINIpaths)
@follows(tsvName)
@originate(tsv_example)
#@mkdir('pq_results') # Create a folder and place results there if needed
def getPandasDF(outfile):
    '''
    Call a python example script from project_quickstart to create a pandas dataframe
    '''
    py_exec = get_py_exec()
    project_scripts_dir = getINIpaths()

    statement = '''
                python %(project_scripts_dir)s/pq_example.py \
                                                       --createDF \
                                                       -O %(outfile)s ;
                touch %(outfile)s
                '''
    # execute command contained in the statement.
    # The command will be sent to the cluster (by default, but this can be
    # turned off with --local).  The statement will be
    # interpolated with any options that are defined in in the
    # configuration files or variable that are declared in the calling
    # function.
    # For example, %(infile)s will we substituted with the
    # contents of the variable "infile"
    # py_exec provides the basename of the directory where the project scripts
    # live.
    P.run(statement) # run() lives in cgat/CGAT/Experiment.py

@follows(tsvName, getPandasDF)
def renameList():
    '''
    Rename list of tsv files being passed to facilitate Ruffus reading and
    tracking.
    '''
    tsv_example = tsvName()
    tsv_example_full = []

    for f in tsv_example:
        f = str(f + '.tsv')
        tsv_example_full.append(f)

    return(tsv_example_full)

tsv_example_full = renameList()

@follows(renameList)
@transform(tsv_example_full, regex(r'(.*).tsv'), r'\1.pq_example.touch', r'\1')
# See Ruffus: http://www.ruffus.org.uk/decorators/transform.html
def run_pq_examples(infile, touchFile, outname):
    '''
    '''
    # command line statement to execute, to run in bash:
    # touch %(outfile)s gives Ruffus a timestamp, not the most elegant way but
    # helpful if there are multiple outputs from a script

    py_exec = get_py_exec()
    project_scripts_dir = getINIpaths()

    statement = '''
                Rscript %(project_scripts_dir)s/pq_example.R -I %(infile)s \
                                                             -O %(outname)s ;
                Rscript %(project_scripts_dir)s/plot_pq_example_pandas.R \
                                                            -I %(infile)s ;
                touch %(touchFile)s
                '''
    P.run(statement)


@follows(run_pq_examples)
@transform(tsv_example, regex(r'(.*)'), r'\1.multiPanel.touch')
def pandasMultiPanel(infile, outfile):
    '''
    Creates a multi-panel figure from the plots generated from
    pq_example.R and plot_pq_example_pandas.R
    '''

    py_exec = get_py_exec()
    project_scripts_dir = getINIpaths()

    statement = '''
                %(py_exec)s %(project_scripts_dir)s/svgutils_pq_example.py \
                              --plotA=%(infile)s_gender_glucose_boxplot.svg \
                              --plotB=%(infile)s_age_histogram.svg \
                              -O F1_%(infile)s ;
                touch %(outfile)s ;
                '''
    P.run(statement)


# Make sure the python executable and project scripts dir are set:
@follows(get_py_exec, getINIpaths)
@originate('run_mtcars_R.touch')
def run_mtcars(outfile):
    '''
    A second set of examples from project_quickstart
    Some plots and an html table of a linear regression are generated.
    '''
    # Plot simple examples with python:
    #statement = '''
    #            %(py_exec)s %(project_scripts_dir)s/plot_pq_example.py ;
    #            touch %(outfile)s
    #            '''

    # R scripts for mtcars dataset example:

    project_scripts_dir = getINIpaths()

    statement = '''
                Rscript %(project_scripts_dir)s/pq_example_mtcars.R ;
                Rscript %(project_scripts_dir)s/plot_pq_example_mtcars.R ;
                touch %(outfile)s
                '''
    P.run(statement)


@follows(run_mtcars)
@originate('F1_mtcars.multiPanel.touch', 'F2_mtcars.multiPanel.touch')
def mtcarsMultiPanel(outfile1, outfile2):
    '''
    Generate a multi-panel plot from existing svg files using the svgutils
    python package. Plots can be generated by run_mtcars().
    '''

    py_exec = get_py_exec()
    project_scripts_dir = getINIpaths()

    statement = '''
                %(py_exec)s %(project_scripts_dir)s/svgutils_pq_example.py \
                                      --plotA=mtcars_cyl_wt_boxplot_2.svg \
                                      --plotB=mtcars_hp_qsec_scatterplot.svg \
                                      -O F1_mtcars ;
                touch %(outfile1)s ;
                %(py_exec)s %(project_scripts_dir)s/svgutils_pq_example.py \
                                          --plotA=mtcars_wt_histogram.svg  \
                                          --plotB=mtcars_boxplot_lm.svg \
                                          -O F2_mtcars ;
                touch %(outfile2)s
                '''
    P.run(statement)

################


################
# Create a pipeline target (call) that will run the full pipeline
# These targets follow all other targets so 'full' will print them out when
# doing:
# python ../code/pq_example/pipeline_pq_example/pipeline_pq_example.py show full --local -v 3
@follows(pandasMultiPanel, mtcarsMultiPanel)
def full():
    pass
################


################
# Specify function to create reports pre-configured with sphinx-quickstart:
report_dir = 'pipeline_report'
@follows(mkdir(report_dir))
#@follows(full)
def make_report():
    ''' Generates html and pdf versions of restructuredText files
        using sphinx-quickstart pre-configured files (conf.py and Makefile).
        Pre-configured files need to be in a pre-existing report directory.
        Existing reports are overwritten.
    '''
    report_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               'pipeline_report'
                                               ))
    print('Copying report templates from: {}'.format(report_path))

    if (os.path.exists(report_dir) and
            os.path.isdir(report_dir) and not
            os.listdir(report_dir)):
        statement = '''cp %(report_path)s/* pipeline_report ;
                       cd pipeline_report ;
                       make html ;
                       ln -sf _build/html/report_pipeline_pq_example.html . ;
                       make latexpdf ;
                       ln -sf _build/latex/pq_example.pdf .
                    '''
        E.info("Building pdf and html versions of your rst files.")
        P.run(statement)

    elif (os.path.exists(report_dir) and
            os.path.isdir(report_dir) and
            os.listdir(report_dir)):
        sys.exit(''' {} exists, not overwriting. You can manually run:
                       make html ;
                       ln -sf _build/html/report_pipeline_pq_example.html . ;
                       make latexpdf ;
                       ln -sf _build/latex/pq_example.pdf .
                       Or delete the folder and re-run make_report
                 '''.format(report_dir))

    else:
        sys.exit(''' The directory "pipeline_report" does not exist.
                     Are the paths correct?
                     Template files were tried to be copied from:
                     {}
                     You can also manually copy files and run "make html" or
                     "make latexpdf".
                 '''.format(report_path))

    return
################


################
if __name__ == "__main__":
    sys.exit(P.main(sys.argv))
################
