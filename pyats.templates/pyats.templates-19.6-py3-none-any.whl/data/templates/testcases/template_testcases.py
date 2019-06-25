#*******************************************************************************
#*                              Template Testcases
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
#*  This file contains some template testcases used by template base and variant
#*  script. It serves as an example demonstrating the usage & benefits of using
#*  testcase files.
#*
#* Note:
#*   instead of duplicating information, this template file will only expand
#*   on details where necessary. You may refer to template.py for details.
#*
#* Note Also:
#*   the use of testcase files, and its ideas, are software development
#*   methodologies, and an optional use-case of pyATS testscripts.
#*
#* Read More:
#*   For the complete and up-to-date user guide on AEtest template, visit:
#*   URL= http://wwwin-pyats.cisco.com/documentation/html/aetest/index.html
#*
#*******************************************************************************

'''template_testcases.py

< describe your testcases >

Arguments:
    <name> (<type>): <description of your testscript argument>

Testcases:
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
from pyats import aetest

#**********************************
#* Using Local Library
from libs import template_library

#*******************************************************************************
#* TESTCASE DEFINITIONS
#*
#*  the testcase bodies defined here are to be inherited from your main scripts.
#*  any testcase data required should be clearly outlined in its headers, so
#*  that when inherited, such data can be provided in the actual testscript.
#*
class TemplateTestcase(aetest.Testcase):
    '''TemplateTestcase

    < docstring description of this testcase >

    Arguments:
        < data required to run this testcase >
    '''

    #**********************************
    #* Setup Section
    #* 
    #*  setup section is optional within each Testcase. It is always run if
    #*  defined. If the setup section's result is not Passed, Passx or Skipped,
    #*  all test sections will be skipped as a consequence.
    @aetest.setup
    def setup(self):
        '''Testcase Setup

        < docstring description of this Setup >
        '''

        pass

    #**********************************
    #* Test Section
    #* 
    #*  each testcase contains one or more tests. Each test is run one after
    #*  the other, in their defined order. 
    @aetest.test
    def template_test(self, steps):
        '''template test

        < docstring description of this test >
        '''

        #**********************************
        #* Testcase Steps
        #*
        #*  testcases should always leverage the steps feature of AEtest. Doing
        #*  so provides more visual clues of the actions taken of each section
        #*  and so on. 
        #*
        #*  Steps is applicable to subsections, setups, tests and cleanups.

        with steps.start('step description of step one'):
            pass

        with steps.start('step demo function call') as step:
            template_library.template_library_function(step)

        with steps.start('step description of step three'):
            pass
        # ... etc

    #**********************************
    #* Cleanup Section
    #*
    #*  always run last in a testcase, the cleanup section is optional, and,
    #*  when defined, runs regardless of previous testcase/setup pass/fail 
    #*  results.
    @aetest.cleanup
    def cleanup(self):
        '''template cleanup

        < docstring description of this cleanup >
        '''

        pass
   