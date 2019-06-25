#*******************************************************************************
#*                           Test Script Template
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
#*   This template file describes how to write a standard base testscript,
#*   supporting data-driven testing, multiple variants & inheritances.
#*
#* Read More:
#*   For the complete and up-to-date user guide on AEtest template, visit:
#*   URL= http://wwwin-pyats.cisco.com/documentation/html/aetest/index.html
#*
#*******************************************************************************

#*******************************************************************************
#* DOCSTRINGS
#*
#*   All test scripts should use the built-in Python docstrings functionality
#*   to define script/class/method headers.
#*
#* Format:
#*   Docstring format should follow:
#*   URL= https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
#*
#* Read More:
#*   Python Docstrings, PEP 257:
#*   URL= http://legacy.python.org/dev/peps/pep-0257/
#*******************************************************************************
'''template.py

< describe your testscript >

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

#*******************************************************************************
#* OPTIONAL AUTHOR INFORMATION
#*
#*   format:
#*      __author__ = '<first> <last> <email>'
#*      __copyright__ = 'Copyright 2015, Cisco Systems'
#*      __credits__ = ['<list>', '<of>', '<names>']
#*      __maintainer__ = '<team owning/maintaining this script>'
#*      __email__ = '<email of owners>''
#*      __date__= '<last modified date>'
#*      __version__ = <decimal version string>
#*
#*******************************************************************************

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


#*******************************************************************************
#* IMPORTS
#*
#*   import all modules that are needed in your test script here. Use some
#*   form of sorting to make it easy to read.
#*
#* Convention:
#*   - one module per import for clarity
#*   - sort imports either alphabetically or per length to give ease of reading,
#*     also try to differentiate by functionality/distributor
#*
#* Example:
#*   import os
#*   import sys
#*   from pyats import tcl
#*   from pyats import aetest
#*
#* Read More:
#*   Python Import System
#*   URL= https://docs.python.org/3/reference/import.html
#*******************************************************************************

#
# imports statements
#
import logging

from pyats import aetest

#******************************
#* Import Testcases Module
#*
#*  import the testcases to be inherited & used by this testscript.
from testcases import template_testcases

#*******************************************************************************
#* LOGGING
#*
#*   Logging should be done by using the standard Python logging module. AEtest
#*   and Easypy will take care of configuring the log outputs to be ATS/TRADe
#*   format. There's not much more to say beyond that. :-)
#*
#* Convention:
#*   The name of your logger should always be set to the name of your script
#*   module, eg, using __name__
#*
#* Note:
#*   pyats.logger.utils provides some logging utilities, such as banners & etc
#*
#* Example:
#*   logger = logging.getLogger(__name__)
#*   logger.info('this is an info message')
#*   logger.error('this is an error message')
#*   logger.warning('this is a warning message')
#*   logger.debug('this is a debug message')
#*   logger.critical('this is a critical message')
#*
#* Read More:
#*   Python Logging HOWTO
#    URL = https://docs.python.org/3.4/howto/logging.html
#*******************************************************************************

#
# create a logger for this module
#
logger = logging.getLogger(__name__)

#*******************************************************************************
#* TESTSCRIPT PARAMETERS
#*
#*  testscripts are driven by data. These data are called 'parameters' within
#*  AEtest scripts. Parameters follows a predefined inheritance rule:
#*      - child section parameters inherits parent section parameters.
#*
#*  this relationship can be charted as (<- denoting parent of):
#*
#*      TestScript <- CommonSetup   <- Subsections
#*           \---- <- Testcase      <- Setup/Test/Cleanup
#*            `--- <- CommonCleanup <- Subsections
#*
#*  or, in set theory, using TestScript/CommonSetup/Subsection as example:
#*          +----------------------------------------------+
#*          | +-----------------------------+  Subsections |
#*          | | +------------+  CommonSetup |   parameters |
#*          | | | TestScript |   parameters |              |
#*          | | | parameters |              |              |
#*          | | +------------+              |              |
#*          | +-----------------------------+              |
#*          +----------------------------------------------+
#*
#*  to define TestScript parameter defaults, create a dictionary named
#* 'parameters' directly within your testscript.
#*      parameters = {
#*          <keys>: <values>,
#*      }
#*
#*  if this testscript was called with script arguments (provided to AEtest),
#*  these script arguments are updated into this TestScript parameter
#*  dictionary (overwriting any conflicting ones).
#*
#* Note:
#*   this is the equivalent of GA/test_params array in Tcl-AEtest scripts.
#*
#* Read More:
#*    http://wwwin-pyats.cisco.com/documentation/html/aetest/parameters.html
#*******************************************************************************

#
# testscript default parameters
#
parameters = {
    '<name>': '<value>',
}

#*******************************************************************************
#* COMMON SETUP SECTION
#*
#*  use common setup section to configure and perform the initial setup of your
#*  testscript environment. All common configurations & etc shared among your
#*  script testcases shall be configured here.
#*
#*  Example:
#*    - check that all required parameters/script arguments are provided
#*    - verify the required topology is present.
#*    - connect to all testbed devices
#*    - check that all configured devices are ready to go
#*    - if there is any failure encountered at this stage, block testcases from
#*      further execution and exit gracefully
#*    - After the mandated checks pass, apply base configuration that is
#*      applicable for the following testcases
class CommonSetup(aetest.CommonSetup):
    '''Common Setup Section

    < common setup docstring >

    Subsections:
        < list the # of subsections and their intentions >

        < subsection > : < descriptions >
    '''

    #******************************
    #* subsection: check parameters
    #*
    #*  suggested subsection. use this subsection to check that your script's
    #*  required arguments & parameters are indeed provided to the testscript.
    @aetest.subsection
    def check_parameters(self, **parameters):
        '''Checking Parameters

        < docstring >

        Arguments:
            < list the mandatory arguments/parameters verified by this script >
        '''

        mandatory_parameters = [
            'testbed',
            #* < and any other mandatory parameters >
        ]
        for parameter in mandatory_parameters:
            assert parameter in parameters, "missing mandated parameter '%s'" \
                                            % parameter


    #******************************
    #* subsection: squeeze topology
    #*
    #*  Optional subsection. Use this subsection to request that only
    #*  wanted devices and links are kept in the topology.
    #*  Device and link aliases are respected.
    #*  All interfaces connected to wanted links and the devices that
    #*  contain them are kept in the topology.
    #*
    #*  All unwanted devices, links and interfaces are removed
    #*  from the topology.
    @aetest.subsection
    def squeeze_topology(self, testbed, **parameters):
        '''Squeezing Topology

        < docstring >
        '''

        # skip this subsection if no testbed was provided
        if not testbed:
            self.skipped('no testbed was provided')

        squeeze_list = []

        if 'routers' in parameters:
            squeeze_list += list(parameters['routers'])

        if 'links' in parameters:
            squeeze_list += list(parameters['links'])

        testbed.squeeze(*squeeze_list)


    #******************************
    #* subsection: validate topology
    #*
    #*  suggested subsection. use this subsection to verify that the provided
    #*  topology, links & devices are present.
    @aetest.subsection
    def validate_topology(self, testbed, **parameters):
        '''Validating Topology

        < docstring >
        '''

        # skip this subsection if no testbed was provided
        if not testbed:
            self.skipped('no testbed was provided')

        # verify all routers exists
        if 'routers' in parameters:
            for rtr in parameters['routers']:
                assert rtr in testbed, 'testbed missing router: %s' % rtr

        # convert labels to devices
        if 'labels' in parameters:
            for label, hostname in parameters['labels'].items():
                parameters['labels'][label] = testbed.devices[hostname]

        # validate links are all there
        if 'links' in parameters:
            link_names = [link.name for link in testbed.links]

            for link in parameters['links']:
                assert link in link_names, "Link missing: %s"  % link

        # etc.

    #******************************
    #* subsection: connect to devices
    #*
    #*  suggested subsection. use this subsection to connect to your testbed
    #*  devices and verify connection is up
    @aetest.subsection
    def connect_to_devices(self, testbed):
        '''Connect to Devices

        < docstring >
        '''

        # skip this subsection if no testbed was provided
        if not testbed:
            self.skipped('no testbed was provided')

        # connect to devices
        for device in testbed:
            device.connect()

            assert device.connected, "Could not connect to device: %s" % device

    #******************************
    #* subsection: configure_interfaces
    #*
    #*  configure your device interfaces
    @aetest.subsection
    def configure_interfaces(self, testbed):
        '''Configure Device Interfaces

        < docstring >
        '''

        #***********************************************************************
        #* Dynamic IP Address Generation
        #*
        #*  It is strongly suggested that device interface IP addresses be
        #*  dynamically generated as part of the common setup section. This can
        #*  be easily accomplished using Python 'ipaddress' module.
        #*
        #*  store the generated ip addresses information into interface object's
        #*  'ipv4' and 'ipv6' attributes. Note that the stored values should
        #*  be ipaddress.IPv4Address and ipaddress.IPv6Address objects instead
        #*  of string values.
        #*
        #*  Refer to ipaddress module for more information
        #*      https://docs.python.org/3/library/ipaddress.html
        #***********************************************************************

        #* < configure device interface code >
        #*
        #*  eg:
        #*      for device in testbed:
        #*          for interface in device:
        #*              device.configure(...)

    #******************************
    #* subsection: configure_tgen
    #*
    #*  configure your traffic generators, if any
    @aetest.subsection
    def configure_tgen(self, **parameters):
        '''Configure Traffic Generators

        < docstring >
        '''

        if 'tgns' in parameters:
            #* < configure tegn code >
            #*
            #*  eg:
            #*      for tgn in parameters['tgen']:
            #*          ...
            pass

    #******************************
    #* subsection: base_configs
    #*
    #*  apply base configurations to your devices
    @aetest.subsection
    def base_configs(self, testbed):
        '''Apply base configurations to your testbed devices

        < docstring >
        '''

        #* < apply base configs to device >
        #*
        #*  eg:
        #*      for device in testbed:
        #*          device.configure(...)


    #**********************************
    #* Any Other Subsections
    #*
    #*  use the following template for any further subsections that you need
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
#*  all testcase codes should be properly defined in the testcases/ folder. This
#*  section is intended for only defining the data and referencing this library
#*  of testcases through basic inheritance.
#*
#*  the end goal is to be able to decouple testscripts from their testcases, and
#*  promote sharing of testcase functions and classes through modular design &
#*  proper documentation.
#*
#*  Note:
#*      This is a template guideline, not a mandated requirement. Testcases
#*      defined inline of their testscripts are still valid. However, this often
#*      leads to long testscripts, plagued with hard-coding and insufficient
#*      abstraction.
#*      The template intends to demonstrate good scripting methodologies, and
#*      thus, demonstrates below that testcases bodies should be defined within
#*      a central, library of testcases, and that the testscripts should only
#*      be referencing them & providing them sufficient data to run.
class ExampleTestcase(template_testcases.TemplateTestcase):
    '''ExampleTemplateTestcase

    < docstring description of this testcase >

    '''

    #**********************************
    #* Testcase Unique Id, Name & Description
    #*
    #*   Testcase uid should be unique to a test script, and is also used for
    #*   result uploading to TIMS. BElow is their default values:
    #*
    #*      uid             unique id of this Testcase class
    #*      name            alternative descriptive name, default uid
    #*      description     docstring of this Testcase class
    #*
    #*   To set and alternative uid/name/description for each testcase, set the
    #*   Testcase class's 'uid', 'name' and 'description' attributes. Note that
    #*   uid cannot contain spaces.
    #*
    #*   Example:
    #*
    #*      class MyExampleTestcase(aetest.Testcase):
    #*          '''docstring for this testcase'''
    #*
    #*          uid = 'a_new_uid_for_my_example_testcase'
    #*          name = 'my meaningful testcase name'
    #*          description = 'a new description for my example testcase'
    #*
    #*   Note:
    #*      it's best to use to default to using the docstring for testcase
    #*      description

    # set alternative testcase uid
    # uid = '< testcase id >'

    # set a meaningful name to testcase
    # name = '< meaningful testcase name> '

    #**********************************
    #* Testcase Grouping
    #*
    #*  testcase grouping is an optional feature. It allows users to group/tag
    #*  testcases by common names, and enables group executions where only
    #*  a select groups of testcases is run.
    #*
    #*  associate testcases to groups by by setting its 'groups' attribute with
    #*  a list of groups names (strings). By default, testcases are not
    #*  associated to any groups.
    #*
    #*  Read More:
    #*  http://wwwin-pyats.cisco.com/documentation/html/aetest/control.html
    #
    # testcase groups
    #
    groups = ['group_A', 'group_B']

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
#*  use common cleanup section to remove all changes made to the environment
#*  during testscript execution and returning them to their original states.
#*
#*  the common cleanup section should be catch-all: it is always run regardless
#*  of testcase results, and thus should coded such that it perfroms a 'best
#*  attempt' removal of any potential changes, regardless of whether they
#*  actually exists.
#*
#*  consider breaking down common cleanup subsections so that it is the reversed
#*  order of common setup's subsections
class CommonCleanup(aetest.CommonCleanup):
    '''Common Cleanup Section

    < common cleanup docstring >

    Subsections:
        < list the # of subsections and their intentions >

        < subsection > : < descriptions >
    '''

    #**********************************
    #* Subsection Template
    #*
    #*   To use, remove leading #* symbole and fill as required. Be careful of
    #*   indentation as Python is indentation sensitive.
    #*
    #*  def < subsectiop name >(self):
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
#*   If this script is to be executed in standalone mode, e.g.
#*
#*      bash$ cd /path/to/script
#*      bash$ ./script.py
#*
#*   then the following should be added as the last thing in your test script
#*   to enable AEtest to run the test script.
#*******************************************************************************
if __name__ == '__main__':

    #**********************************
    #* Local Imports
    #*
    #*  these imports are here only because they are not required when the
    #*  testscript is normally run, and is only used during standalone runs.
    #*
    #*  this avoids polluting the script namespace

    #
    # local imports
    #
    import argparse
    from pyats import topology

    #**********************************
    #* Log Level
    #*
    #*  set the log level for this run while in standalone mode: you're in
    #*  control of everything.

    #
    # set global loglevel
    #
    logging.root.setLevel('INFO')

    #**********************************
    #* Standalone Parsers
    #*
    #*  in easypy execution, the infrastructure and the job file passes in
    #*  necessary script arguments. To achieve the same effect in standalone
    #*  execution, you need to create script command-line arguments to do the
    #*  same job.
    #*
    #*  use 'argparse' module.
    #*      https://docs.python.org/3.4/library/argparse.html
    #*
    #*  Guidelines:
    #*      - all custom arguments should start with double dash '--'
    #*      - parsing should only ever be done using parse_known_args(), as
    #*        AEtest also parses its argument during main()
    #*
    #*  in the example below, we've added the --testbed argument for you:
    #*  the equivalent of -testbed_file, loading testbed file into topology
    #*  object.

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

    #**********************************
    #* aetest.main()
    #*
    #*  this runs the testscript. Pass in any additional script arguments
    #*  in so that it becomes the base part of your testscript parameters.

    #
    # calling aetest.main() to start testscript run
    #
    aetest.main(testbed = args.testbed)

