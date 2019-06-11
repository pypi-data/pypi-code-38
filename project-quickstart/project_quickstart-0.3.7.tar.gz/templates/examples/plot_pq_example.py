#!/usr/bin/env python3
'''
plot_pq_example.py
==================

:Author: |author_name|
:Release: |version|
:Date: |today|


Purpose
=======

|description|


This script generates boxplot and scatterplot examples.

Usage and options
=================

These are based on docopt_, see examples_.

.. _docopt: https://github.com/docopt/docopt

.. _examples: https://github.com/docopt/docopt/blob/master/examples/options_example.py


Usage:
       plot_pq_example.py [-I FILE] [-O FILE] [--pop=<pop_size>] [--sample=<sample_size>] [--force] [--dry-run]
       plot_pq_example.py [-h | --help] [-v | --version]

Options:
    -I FILE                   Input file name, not used here
    -O FILE                   Output file name, not used here
    --pop=<pop_size>          Population size as integer [default: 100]
    --sample=<sample_size>    Sample size as integer [default: 500]
    -h --help                 Show this screen
    -v --version              Shows the version, not set here
    --force                   Overwrites files, not used here
    --dry-run                 Shows what will happen, not used here

Documentation
=============

    For more information see:

        |url|

'''
############
import sys
import os
from docopt import docopt

import matplotlib.pyplot as plt
import random

# Read docopt options:
options = docopt(__doc__)
############

############

def doBoxplot():
    '''Generate some example data and create a boxplot
       This is modified from
       http://users.ecs.soton.ac.uk/jn2/teaching/pythonLecture.html
    '''

    # Make a first example plot:
    if options['--pop']:
        popSize = int(options['--pop'])
    else:
        popSize = 100

    category1 = []
    category2 = []

    # Start by generating scores for category 1 individuals
    # Their mean score is 95
    for i in range(popSize):
        category1.append(random.normalvariate(95,10))

    # Now generate scores for category 2 individuals
    # They have a higher mean of 105
    for i in range(popSize):
        category2.append(random.normalvariate(105,10))

    scores = [category1,category2]

    plt.boxplot(scores)
    plt.savefig('pyplot_example_boxplots.svg')
    #plt.savefig('boxplots.pdf')
    plt.close()
    return
############

############
def doScatterplot():
    '''Create a scatterplot example
    '''
    x = []
    y = []

    if options['--sample']:
        sampleSize = int(options['--sample'])
    else:
        sampleSize = 500

    for i in range(sampleSize):
        newVal = random.normalvariate(100,10)
        x.append(newVal)
        y.append(newVal / 2.0 + random.normalvariate(50,5))

    plt.scatter(x,y,c="red",marker="s")
    plt.xlabel("Variable 1")
    plt.ylabel("Variable 2")
    plt.savefig("pyplot_example_scatterplot.svg")
    #plt.savefig('scatter2.pdf')
    plt.close()
    return
############

############
# Call functions:
def main():
    doBoxplot()
    doScatterplot()
    return
############

############ 
# Finish and exit with docopt arguments:
if __name__ == '__main__':
    arguments = docopt(__doc__)
    print(arguments)
    sys.exit(main())
############
