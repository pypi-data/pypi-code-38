#*******************************************************************************
#*                       Test Script Variant Template
#* ----------------------------------------------------------------------------
#* ABOUT THIS TEMPLATE - Please read
#*
#* - Any comments with "#*" in front of them (like this entire comment box) are
#*   for template clarifications only and should be removed from the final
#*   product.
#*
#* - Anything enclosed in <> must be replaced by the appropriate text for your
#*   application
#*
#* Author:
#*    Siming Yuan, Automation Strategy - Core Software Group (CSG)
#*
#* Support:
#*    pyats-support@cisco.com
#*
#* Description:
#*   This template file describes the variant testscripts, what they are, why
#*   they should be used, and so on. It builds knowledge and understanding based
#*   on the template.py file.
#*
#* Note:
#*   instead of duplicating information, this template file will only expand
#*   on details where necessary. You may refer to template.py for details.
#*
#* Read More:
#*   For the complete and up-to-date user guide on AEtest template, visit:
#*   URL= http://wwwin-pyats.cisco.com/documentation/html/aetest/index.html
#*
#*******************************************************************************

#*******************************************************************************
#* VARIANT SCRIPTS
#*
#*
#*  This is called the 'variant' script: it provides varianting (eg, extends, 
#*  adds more to) to the base script. Variant scripts reuses the CommonSetup
#*  and CommonCleanup sections of the original script (and may choose to extend
#*  it further with more subsections), and runs similar testcases with a set 
#*  of different data.
#*
#*  Keep in mind that a variant is still another valid testscripts. It simply
#*  contains minimal data, and maximizes reusing of other testscript components.
#*
#*  The base idea here is to be able to modularize testing into different
#*  scripts whilst maintaining the least amount of codes possible through proper
#*  software development/reuse techniques.
#*
#*  Some Variant Examples:
#*      - Scale/Performance
#*      - High Availablility (HA)
#*      - Sanity, Regression
#*      - OS/Platform
#*      - ... etc
#*
#*  Note:
#*      the use of variant, and the idea of variants, are software development
#*      methodologies, and an optional use-case of pyATS testscripts.
#* 
#*******************************************************************************

'''variant_template.py

< describe your variant >

Topology:
    <describe and/or draw your topology here>

Arguments:
    <name> (<type>): <description of your testscript argument>

Examples:
    < provide examples on how to use this test script. >

References:
    < provide references here. >

Notes:
    < provide notes if needed >
'''

# optional author information
__author__ = 'Cisco Systems Inc.'
__copyright__ = 'Copyright (c) 2017, Cisco Systems Inc.'
__contact__ = ['pyats-support@cisco.com', 'pyats-support-ext@cisco.com']
__credits__ = ["Sedy Yadollahi", 
               "Jean-Benoit Aubin", 
               "Ahmad Barghou",
               "Ke Liu"]
__date__= 'June 15, 2015'
__version__ = 2.0

#
# imports statements
#
import logging

from pyats import aetest

from testcases import template_testcases

#******************************
#* Import Base Testscript
#*
#*  as this is a variant script, we need to import the base script in order to
#*  reference its sections.
import template

#
# create a logger for this module
#
logger = logging.getLogger(__name__)

#
# testscript default parameters
#
parameters = {}


class CommonSetup(template.CommonSetup):
    '''Variant CommonSetup

    < common setup docstring >

    Subsections:
        < list the # of subsections and their intentions >
        
        < subsection > : < descriptions >
    '''

    #**********************************
    #* Subsection Extended
    #*
    #*  through inheritance, all subsections from the parent script is already
    #*  picked up. If there are any additional things that needs to be done
    #*  for this variant script, add more subsections.
    #*
    #*  def < subsectiop name >(self, <parameters>):
    #*      '''< descriptive name >
    #*      
    #*       < docstring/description >
    #*      '''
    #*      
    #*      < your code here>
    #*  
    #*      # provide result if necessary
    #*      self.< result >()
    #*


#*******************************************************************************
#* TESTCASES
#*
#*  same as base script, reference all testcases from testcases/ library.
class ExampleTestcase(template_testcases.TemplateTestcase):
    '''ExampleTemplateTestcase

    < docstring description of this testcase >

    '''

    #
    # testcase groups
    #
    groups = ['<group>', '<group>']

    #**********************************
    #* Testcase Data
    #*
    #*  define all the data required for the inherited testcase to operate.
    #*  these data attributes should be define withe the testcase definition.
    #*
    #*      <data> = <value>
    #*
    #*  Example:
    #*      data_one = 'some values for data_one'
    #*      data_two = 'some values for data_two'
    #*      ... etc


#*******************************************************************************
#* COMMON CLEANUP SECTION
#*
class CommonCleanup(aetest.CommonCleanup):
    '''Variant CommonCleanup

    < common setup docstring >

    Subsections:
        < list the # of subsections and their intentions >
        
        < subsection > : < descriptions >
    '''

    #**********************************
    #* Subsection Extended
    #*
    #*  through inheritance, all subsections from the parent script is already
    #*  picked up. If there are any additional things that needs to be done
    #*  for this variant script, add more subsections.
    #*
    #*  def < subsectiop name >(self, <parameters>):
    #*      '''< descriptive name >
    #*      
    #*       < docstring/description >
    #*      '''
    #*      
    #*      < your code here>
    #*  
    #*      # provide result if necessary
    #*      self.< result >()
    #*


#*******************************************************************************
#* STANDALONE EXECUTION
#*
if __name__ == '__main__': 

    #
    # local imports 
    #
    import argparse
    from pyats import topology

    #
    # set global loglevel
    #
    logging.root.setLevel('INFO')

    #
    # local standalone parsing
    #
    parser = argparse.ArgumentParser(description = "standalone parser")
    parser.add_argument('--testbed', dest = 'testbed', 
                        help = 'testbed YAML file',
                        type = topology.loader.load, 
                        default = None)

    # do the parsing
    args = parser.parse_known_args()[0]

    #
    # calling aetest.main() to start testscript run
    #
    aetest.main(testbed = args.testbed)

