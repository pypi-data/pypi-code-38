##!/usr/bin/env python3
'''
pq_example.py
=============

:Author: |author_names|
:Release: |version|
:Date: |today|


Purpose
=======

|description|

This is a template for a python script. It is runnable, grew completely
out of proportion and is now a template and a basic example.

When you use project_quickstart's "--script-python" option for example
you'll get this copy. For now just delete everything in the middle and
write you script.


Usage and options
=================

These are based on docopt_, see examples_.

.. _docopt: https://github.com/docopt/docopt

.. _examples: https://github.com/docopt/docopt/blob/master/examples/options_example.py


Usage:
       pq_example.py [--a_number=<int>]
       pq_example.py (--createDF) [--sample-size=<int>] [-O FILE]
       pq_example.py [-h | --help] [-V | --version]

Options:
    --a_number=<int>    Give a number just for fun
    --createDF          Create a pandas data frame
    --sample-size=<int> Specify a sample size (number of rows) for the dataframe[default: 1000]
    -O FILE             Output file name
    -h --help           Show this screen
    -V --version        Show version

Input:

None

Output:

Prints a few things to screen


Requirements:

Python packages only

Documentation
=============

    For more information see:

        |url|

'''
##############
# Get all the modules needed
# Understanding Python:
#import this

# System:
import os
import sys
import glob

# Options and help:
import docopt

# Data science:
import pandas
#import numpy
import matplotlib.pyplot as plt
import scipy.stats as stats

# required to make iteritems python2 and python3 compatible
from builtins import dict

# Try getting CGAT:
try:
    import CGAT.iotools as iotools
    import CGATPipeline.Pipeline as P
    import CGATPipeline.Experiment as E

except ImportError:
    print('\n', "Warning: Couldn't import CGAT modules, continuing without")
    pass

# Import this project's module, uncomment if building something more elaborate:
#try:
#    import module_pq_example.py

#except ImportError:
#    print("Could not import this project's module, exiting")
#    raise

# Import additional packages:
import string # this is used in the pandas function
import random
##############

##############
#####
# Behaviours to keep in mind:
# http://docs.python-guide.org/en/latest/writing/gotchas/
# https://www.toptal.com/python/top-10-mistakes-that-python-programmers-make
# https://sopython.com/wiki/Common_Gotchas_In_Python
# Some basic Python reminders
# Indexing is 0-based, start included, stop excluded
# PEP8 has 80 character limit and 4 spaces for indentation, do not use tabs, much less mix
# Python operator precedence: https://www.tutorialspoint.com/python/operators_precedence_example.htm
# dictionaries are accessed as my_dict[2] ; '2' == key, not index ; while my_list[2] is an index ; use assert if ambigous
# modulo is % (the remainder) ; // gives the integer of the division
# lists and dictionaries are mutable; tuples immutable

# Some Python pages:
# https://www.python.org/
# https://en.wikipedia.org/wiki/Python_(programming_language)
# http://python.net/~goodger/projects/pycon/2007/idiomatic/handout.html

# Coding in Python:
# http://docs.python-guide.org/en/latest/writing/style/
# https://stackoverflow.com/questions/356161/python-coding-standards-best-practices

# Programming styles
# https://blog.newrelic.com/2015/04/01/python-programming-styles/

# Functional programming in Python:
# https://stackoverflow.com/questions/36504/why-functional-languages?noredirect=1&lq=1
# https://stackoverflow.com/questions/1017621/why-isnt-python-very-good-for-functional-programming
# https://stackoverflow.com/questions/21895525/python-programming-functional-vs-imperative-code

# OOP:
# https://docs.python.org/3/tutorial/classes.html
# https://python.swaroopch.com/oop.html
# https://jeffknupp.com/blog/2014/06/18/improve-your-python-python-classes-and-object-oriented-programming/

# regex
# http://www.diveintopython3.net/regular-expressions.html
# https://docs.python.org/3/howto/regex.html
#####

#####
# If this becomes a more complex project you could move all functions (except
# e.g. main()) to a module.py script.

# Basic function structure:
def my_func(a_number):
    '''
    Comment the function, this will be pulled automatically into the documentation.
    '''

    # Make sure the setup is correct for this function:
    assert True == True
    print('Do something with "a_number"')
    x = a_number
    OK = x * a_number
    return(OK)
#####

#####
def handleErrors():
    ''' A function to handle errors '''
    try:
        print('Pass something')
    except TypeError: #some error to catch
        print('Wrong type of variable') #some helpful message or other option
        raise # Raise the system error anyway
    except: # 'except:' by itself will catch everything, potentially disastrous
        print("Unexpected error:", sys.exc_info()[0])
        raise # even if caught raise the error
    finally:
        print('Did this work?')#do this regardless of the above, also dangerous
#####

#####
def elseIf(a_number):
    ''' A simple function with an if else structure'''
    x = a_number
    if x > 1:
        print('Your number is positive')
    elif x < 1:
        print('Your number is negative')
    else:
        print('You gave a zero')
#####

#####
# Basic OOP class structure:
# Form e.g.: https://www.tutorialspoint.com/python/python_classes_objects.htm
class SuperHero:
    '''
    Common base class for all employees
    '''
    SuperSaves = 0

    def __init__(self, name, power, saves):
       self.name = name
       self.power = power
       self.saves = saves
       SuperHero.SuperSaves += saves

    def displaySaves(self):
      print("Total SuperHero saves %d" % SuperHero.SuperSaves)

    def displaySuperHero(self):
        print("Name: ", self.name,  " Power: ", self.power, " Saves: ", self.saves)

def runOOPHeroes(saves):
    ''' Example function that runs OOP code for SuperHeroes '''
    # First object in class:
    super1 = SuperHero("SuperWoman", 'Strong', saves)
    # Second object in class:
    super2 = SuperHero("AveJoe", 'Common Sense', saves = (saves - 2))

    # Check the Attributes:
    super1.displaySuperHero()
    super2.displaySuperHero()
    print("Total SuperHero saves %d" % SuperHero.SuperSaves)
    return()
#####

#####
# Create a pandas dataframe, run basic stats, lm, table and plots and save to
# disk:
# See pandas in 10 minutes:
# http://pandas.pydata.org/pandas-docs/stable/10min.html

def id_generator(size = 6,
                 chars = string.ascii_uppercase + string.digits,
                 sample_size = 1000):
    ''' Generates a random sequence of letters and numbers and outputs a pandas
        series  of a given sample size that is is
        Modified from:
        https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python?rq=1
    '''
    ID_list = []
    sample_size = sample_size + 1 # Python index is 0-based, stop number is
                                  # excluded
    for i in range(1, sample_size):
        i = ''.join(random.choice(chars) for i in range(size))
        ID_list.append(i)

    ID_list = pandas.Series(ID_list)
    #print(ID_list.head(),
    #      ID_list.tail(),
    #      ID_list.describe(),
    #      )

    return(ID_list)

def number_generator(lower_bound = 0,
                     upper_bound = 1001,
                     mean = 1,
                     sd = 1,
                     sample_size = 1000):
    ''' Generate a set of random values based on a given mean, standard
        deviation, list size and range from a normal distribution.
        The output is a pandas series of a given sample size.
    '''
    # See:
    # https://docs.scipy.org/doc/scipy-0.17.0/reference/generated/scipy.stats.truncnorm.html
    # stackoverflow how-to-specify-upper-and-lower-limits
    # In Python indexing is 0-based (includes the start but excludes the stop)
    sample = stats.truncnorm.rvs(a = lower_bound,
                                 b = upper_bound,
                                 loc = mean,
                                 scale = sd,
                                 size = sample_size)
    sample = pandas.Series(sample)
    #print(sample.head(),
    #      sample.tail(),
    #      sample.describe(),
    #      )

    return(sample)

def bool_generator(sample_size = 1000):
    ''' Generate a list of random values given a size for booleans
        (e.g. male or female).
        The output is a pandas series of a given sample size.
    '''
    gender = []
    sample_size = sample_size + 1
    for n in range(1, sample_size):
        n = random.choice(['male', 'female'])
        gender.append(n)

    gender = pandas.Series(gender)
    #print(gender.head(),
    #      gender.tail(),
    #      gender.describe(),
    #      )
    return(gender)

def createDF(sample_size = 1000, outfile = 'pandas_dataframe_example.tsv'):
    ''' Generate a pandas dataframe that uses random IDs and random values from
        given distributions of four variables.
    '''
    # "Generate a pandas dataframe by passing a dict of objects that can be
    # converted to series-like."
    # These are just numbers, nothing is adjusted, weighted, etc., the means
    # and SDs are arbitrary. Some values though:
    # age: 40.0 average age of the UK population
    # gender: 50.89% in 2011 apparently
    # glucose: Normal Fasting plasma glucose <100 mg/dL (5.6 mmol/L)
    # BMI: roughly 26 in men and women for the UK in 2010
    # Some references:
    # https://en.wikipedia.org/wiki/Demography_of_the_United_Kingdom
    # https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/articles/overviewoftheukpopulation/july2017
    # https://www.uptodate.com/contents/screening-for-type-2-diabetes-mellitus?source=search_result&search=glucose&selectedTitle=1~150#H7
    # http://www.thelancet.com/cms/attachment/2094506084/2077189969/mmc1.pdf
    # https://www.uptodate.com/contents/image?imageKey=ENDO%2F73797&topicKey=ENDO%2F1798&rank=1~150&source=see_link&search=hypoglycemia

    print('\n', 'Sample size is: ', sample_size)
    random_df = pandas.DataFrame({'ID': id_generator(size = 6,
                                                     chars = string.ascii_uppercase + string.digits,
                                                     sample_size = sample_size),
                                  'age': number_generator(lower_bound = 0,
                                                          upper_bound = 121,
                                                          mean = 40.0,
                                                          sd = 20,
                                                          sample_size = sample_size),
                                  'gender': bool_generator(sample_size = sample_size),
                                  'glucose': number_generator(lower_bound = 0,
                                                              upper_bound = 501,
                                                              mean = 80,
                                                              sd = 10,
                                                              sample_size = sample_size),
                                  'BMI': number_generator(lower_bound = 0,
                                                          upper_bound = 205,
                                                          mean = 26,
                                                          sd = 3,
                                                          sample_size = sample_size),
                                  },
                          # Enforce column order as the dataframe comes from a dictionary:
                                  columns = ['ID', 'age', 'gender', 'glucose', 'BMI']
                                  )

    print('\n',
          'The first rows of your data frame are:',
          '\n', '\n',
          random_df.head(),
          '\n', '\n',
          'The last rows of your data frame are:',
          '\n', '\n',
          random_df.tail(),
          '\n', '\n',
          'Some basic stats:'
          '\n', '\n',
          random_df.describe(),
          '\n',
          )

    # Save the file to disk with a default name:
    print('\n', 'Saving the dataframe as a tab separated file: {}'.format(outfile), '\n')
    random_df.to_csv(outfile,
                     sep = '\t',
                     na_rep = 'NA',
                     header = True,
                     )
    return(random_df)
#####
##############

##############
def main():
    ''' with docopt main() expects a dictionary with arguments from docopt()
    docopt will automatically check your docstrings for usage, set -h, etc.
    '''
    version = '"first version" (or e.g. "0.1.1")'
    options = docopt.docopt(__doc__, version = version)
    welcome_msg = str('\n' + 'Welcome to pq_example.py. This is {}' +
            '\n').format(version)
    print(welcome_msg)
    docopt_error_msg = str('\n' + 'pq_example.py exited due to an error.' + '\n')
    docopt_error_msg = str(docopt_error_msg
                           + '\n'
                           + 'Try pq_example.py --help'
                           + '\n' + '\n'
                           + 'Options in place:'
                           + '\n'
                           + str(options)
                           + '\n'
                           )

    try:
        if options['--a_number'] and len(options['--a_number']) > 0:
            a_number = str(options['--a_number']).strip('[]').strip("''")
            a_number = int(a_number)
            print('\n', 'Your chosen number for SuperHeroes is: {}'.format(a_number))
            print('\n', ''' This number will also be used for the elseIf
                            function example.
                        ''')
            # Call all the functions described above here:
            my_func(a_number)
            elseIf(a_number = a_number)
            handleErrors()
            runOOPHeroes(saves = a_number)
            print('\n', "Ran some tests above and finished succesfully. That's all.")

        elif options['--createDF']:
            # Repeat defaults here (these will override previous ones) to avoid
            # complicated options combinations:
            outfile = 'pandas_dataframe_example.tsv'
            sample_size = 1000

            if not options['--sample-size']:
                print(''' Using default values for sample size to create a pandas
                          dataframe.''')

            elif (options['--sample-size'] and
                    len(options['--sample-size']) > 0):
                sample_size = str(options['--sample-size']).strip('[]').strip("''")
                sample_size = int(sample_size)
                print('\n', 'Your sample size for the pandas dataframe is: {}'.format(sample_size))

            if options['-O'] and len(options['-O']) > 0:
                outfile = str(options['-O']).strip('[]').strip("''")
                outfile = str(outfile + '.tsv')
                print('Saving your dataframe with the name: {}'.format(outfile))

            createDF(sample_size = sample_size, outfile = outfile)

        else:
            print(docopt_error_msg)
            print(''' Did you provide a number for --a_number?
                      Did you ask for the --createDF option?
                      Is your --sample-size an integer and greater than 0?
                      Exiting...
                  ''')
            sys.exit()

    # Handle exceptions:
    except docopt.DocoptExit:
        print(docopt_error_msg)
        raise
##############


##############
# Finish and exit with docopt arguments:
if __name__ == '__main__':
    sys.exit(main())
##############
