import datetime
import importlib
import imp
import inspect
import itertools
import logging
import os
import pickle
import sys
import time
import traceback
import types
from unittest import SkipTest

import nose
import nose.case
import nose.config
import nose.plugins

from slickqa import SlickQA, Testcase, ResultStatus, RunStatus, Step, Result, make_result_updatable, \
    make_testrun_updatable, DocStringMetaData, GraphValueReference
from slickqa.connection import SlickConnection

try:
    from ConfigParser import SafeConfigParser
except:
    from configparser import SafeConfigParser

__author__ = 'jcorbett'

log = logging.getLogger('nose.plugins.snot')

current_result = None
""":type: Result"""
testrun = None
config = None
logs = []
on_file_result = None
snot_options = None
test_failed = False
test_not_tested = False

REQUIRES_ATTRIBUTE = 'slick_requires'


class PassedOnRetry(Exception):
    pass

class NotTested(SkipTest):
    global test_not_tested
    test_not_tested = True
    pass

class Requirements(list):
    pass


def requires(*args):
    def _wrap_with_requires(f):
        if hasattr(f, REQUIRES_ATTRIBUTE):
            (getattr(f, REQUIRES_ATTRIBUTE)).extend(args)
        else:
            setattr(f, REQUIRES_ATTRIBUTE, args)
        return f
    return _wrap_with_requires


def add_file(path, fileobj=None):
    """
    Upload a file to slick, adding it to the current test result.  If no test is running, this will do nothing!

    :param path: The path to the specified file
    :return: Nothing
    """
    if current_result is not None:
        current_result.add_file(path, fileobj)


def add_link(name, url):
    """
    Add a link to the current result.
    :param name: the name of the link, this is what get's displayed
    :param url: the URL of the link for putting in an html a tag href attribute
    :return: nothing
    """
    if current_result is not None:
        current_result.add_link(name, url)


def add_link_to_testrun(name, url):
    """
    Add a link to the current testrun.
    :param name: the name of the link, this is what get's displayed
    :param url: the URL of the link for putting in an html a tag href attribute
    :return: nothing
    """
    if testrun is not None:
        testrun.add_link(name, url)


def add_file_to_testrun(path, fileobj=None):
    """
    Upload a file to slick, adding it to the current testrun.  If there is no current slick testrun this will do
    nothing!

    :param path: The path to the specified file
    :return: Nothing
    """
    if testrun is not None:
        testrun.add_file(path, fileobj)


def add_graph(graph):
    """
    Add a graph attribute to slick result
    :param graph: {'columns': [{'type': str, 'name': str}], 'values': [{'date': date_in_millis, 'measurements': [1, 2, 3, 4]}]}
    :return: Nothing
    """
    if current_result is not None:
        current_result.graph = graph
        current_result.update()


def write_to_graph(value):
    """
    Append value to graph object
    :param value: {'date': date_in_millis, 'measurements':[1, 2, 3, 4]}
    :return: Nothing
    """
    try:
        if current_result is not None:
            if isinstance(value, (list, tuple)):
                current_result.graph.values.extend([GraphValueReference.from_dict(v) for v in value])
            else:
                current_result.graph.values.append(GraphValueReference.from_dict(value))
            current_result.update()
    except:
        log.warn("Error while trying to write to graph. Catching. Don't care.")


def parse_config(files):
    parser = SafeConfigParser()
    parser.read(files)
    return parser


def call_function(function_name):
    module = None
    if '.' not in sys.path:
        sys.path.append('.')
    if '.' in function_name:
        last_dot_index = function_name.rindex('.')
        module = function_name[:last_dot_index]
        function_name = function_name[last_dot_index + 1:]
    if module is None:
        module = globals()
    else:
        module = importlib.import_module(module)
    if hasattr(module, function_name):
        func = getattr(module, function_name)
        return func()
    else:
        raise Exception("could not find " + function_name + " to run.")


class LogCapturingHandler(logging.Handler):

    ignore = ['nose', 'slick', 'requests']

    def __init__(self):
        super(LogCapturingHandler, self).__init__()

    def pylevel_to_slicklevel(self, loglevel):
        if loglevel == logging.DEBUG:
            return "DEBUG"
        elif loglevel == logging.INFO:
            return "INFO"
        elif loglevel == logging.WARN:
            return "WARN"
        elif loglevel > logging.WARN:
            return "ERROR"
        else:
            return "DEBUG"

    def emit(self, record):
        for ignore_name in LogCapturingHandler.ignore:
            if record.name.startswith(ignore_name) and not record.name.startswith('slickwd'):
                return
        msg = self.format(record)
        if current_result is not None:
            if record.exc_info is None:
                current_result.add_log_entry(msg,
                                             level=self.pylevel_to_slicklevel(record.levelno),
                                             loggername=record.name)
            else:
                excmessage = ''
                if hasattr(record.exc_info[1], 'message'):
                    excmessage = record.exc_info[1].message
                current_result.add_log_entry(msg,
                                             level=self.pylevel_to_slicklevel(record.levelno),
                                             loggername=record.name,
                                             exceptionclassname=record.exc_info[0].__name__,
                                             exceptionmessage=excmessage,
                                             stacktrace=traceback.format_tb(record.exc_info[2]))


class SlickAsSnotPlugin(nose.plugins.Plugin):
    name = "snot"
    score = 1800
    testruns = dict()

    def options(self, parser, env=os.environ):
        super(SlickAsSnotPlugin, self).options(parser, env=env)
        parser.add_option("--slick-url", action="store", default=env.get('SLICK_URL'),
                          metavar="SLICK_URL", dest="slick_url",
                          help="the base url of the slick web app [SLICK_URL]")
        parser.add_option("--slick-project-name", action="store", default=env.get('SLICK_PROJECT_NAME'),
                          metavar="SLICK_PROJECT_NAME", dest="slick_project_name",
                          help="the name of the project in slick to use [SLICK_PROJECT_NAME]")
        parser.add_option("--slick-release", action="store", default=env.get('SLICK_RELEASE'),
                          metavar="SLICK_RELEASE", dest="slick_release",
                          help="the release under which to file the results in slick [SLICK_RELEASE]")
        parser.add_option("--slick-build", action="store", default=env.get('SLICK_BUILD'),
                          metavar="SLICK_BUILD", dest="slick_build",
                          help="the build under which to file the results in slick [SLICK_BUILD]")
        parser.add_option("--slick-build-from-function", action="store", default=env.get('SLICK_BUILD_FROM_FUNCTION'),
                          metavar="SLICK_BUILD_FROM_FUNCTION", dest="slick_build_from_function",
                          help="get the slick build from a function.  The parameter should be the module and function name to call [SLICK_BUILD_FROM_FUNCTION].")
        parser.add_option("--slick-testplan", action="store", default=env.get('SLICK_TESTPLAN'),
                          metavar="SLICK_TESTPLAN", dest="slick_testplan",
                          help="the testplan to link the testrun to in slick [SLICK_TESTPLAN]")
        parser.add_option("--slick-testrun-name", action="store", default=env.get('SLICK_TESTRUN_NAME'),
                          metavar="SLICK_TESTRUN_NAME", dest="slick_testrun_name",
                          help="the name of the testrun to create in slick [SLICK_TESTRUN_NAME]")
        parser.add_option("--slick-environment-name", action="store", default=env.get('SLICK_ENVIRONMENT_NAME'),
                          metavar="SLICK_ENVIRONMENT_NAME", dest="slick_environment_name",
                          help="the name of the environment in slick to use in the testrun [SLICK_ENVIRONMENT_NAME]")
        parser.add_option("--slick-testrun-group", action="store", default=env.get('SLICK_TESTRUN_GROUP'),
                          metavar="SLICK_TESTRUN_GROUP", dest="slick_testrun_group",
                          help="the name of the testrun group in slick to add this testrun to (optional) [SLICK_ENVIRONMENT_NAME]")
        parser.add_option("--slick-agent-name", action="store", default=env.get('SLICK_AGENT_NAME'),
                          metavar="SLICK_AGENT_NAME", dest="slick_agent_name",
                          help="what to put in slick's hostname field in the result.")
        schedule_results_default = "normal"
        if 'SLICK_SCHEDULE_RESULTS' in env:
            schedule_results_default = "schedule"
        parser.add_option("--slick-schedule-results", action="store_const", const="schedule", default=schedule_results_default,
                          metavar="SLICK_SCHEDULE_RESULTS", dest="slick_mode",
                          help="Schedule empty results in slick, but do not run the tests")
        parser.add_option("--slick-sequential-testrun", action="store_const", const="sequential_testrun", default=False,
                          metavar="SLICK_SEQUENTIAL_TESTRUN", dest="sequential_testrun",
                          help="Schedule empty results in slick, but do not run the tests")
        parser.add_option("--slick-schedule-add-requirement", action="append", default=[],
                          metavar="SLICK_SCHEDULE_ADD_REQUIREMENT", dest="requirement_add",
                          help="Add a requirement to all results when scheduling.")
        parser.add_option("--slick-schedule-add-attribute", action="append", default=[],
                          metavar="SLICK_SCHEDULE_ADD_ATTRIBUTE", dest="attribute_add",
                          help="Add an attribute to all results when scheduling.")
        parser.add_option("--slick-schedule-new-requires", action="store_true", dest="new_requires",
                          help="apply the requires directly on the result as an attribute.")
        parser.add_option("--slick-testrun-id", action="store", default=env.get('SLICK_TESTRUN_ID'),
                          metavar="SLICK_TESTRUN_ID", dest="slick_testrun_id",
                          help="Instead of creating a new testrun, use an existing one.")
        parser.add_option("--slick-result-id", action="store", default=env.get('SLICK_RESULT_ID'),
                          metavar="SLICK_RESULT_ID", dest="slick_result_id",
                          help="Instead of creating a new result in the testrun, update an existing one.")
        parser.add_option("--snot-no-log-capture", dest="snot_no_log_capture", default=env.get('SNOT_NO_LOG_CAPTURE'),
                          metavar="SNOT_NO_LOG_CAPTURE", action="store_const", const=True,
                          help="Don't capture the logs from the logging framework")
        parser.add_option("--slick-organize-by-tag", action="append", default=None,
                          help='A space delimited list of tag keys to base test run names after. Will be " - " delimited.')
        parser.add_option("--slick-duplicate", action="store", default=None, dest="slick_duplicate",
                          help='Duplicate each test x number of times.')

        # Make sure the log capture doesn't show slick related logging statements
        if 'NOSE_LOGFILTER' in env:
            env['NOSE_LOGFILTER'] = env.get('NOSE_LOGFILTER') + ",-slick,-requests,-slick-reporter"
        else:
            env['NOSE_LOGFILTER'] = "-slick,-requests,-slick-reporter"

    def configure(self, options, conf):
        super(SlickAsSnotPlugin, self).configure(options, conf)
        assert isinstance(conf, nose.config.Config)
        global config
        global snot_options
        snot_options = options
        if options.files is not None and len(options.files) > 0:
            config = parse_config(options.files)
        if not self.enabled:
            return
        self.options = options

        if not (hasattr(options, 'slick_testrun_id') and hasattr(options, 'slick_result_id') and options.slick_testrun_id is not None and options.slick_result_id is not None):
            for required in ['slick_url', 'slick_project_name']:
                if (not hasattr(options, required)) or getattr(options, required) is None or getattr(options, required) == "":
                    log.error("You can't use snot without specifying at least the slick url and the project name.")
                    self.enabled = False
                    return

    def addSlickTestrun(self, testplan_name=None, requirements=None):
        global config, testrun
        options = self.options
        if testplan_name:
            self.testplan = testplan_name
        if self.testplan and self.testplan in self.testruns:
            self.testrun_id = self.testruns[self.testplan]
        if self.build_function:
            try:
                self.build = call_function(self.build_function)
            except:
                log.warn("Problem occured calling build information from '%s': ", self.build_function, exc_info=sys.exc_info())
        testrun = None
        if self.testplan and self.testplan in self.testruns:
            self.slick = self.testruns[self.testplan]
            testrun = self.slick.testrun
            if self.mode == 'schedule':
                if self.sequential_testrun and requirements:
                    if not hasattr(testrun, 'requirements'):
                        testrun.requirements = []
                    testrun.requirements.extend(requirements)
                    testrun.requirements = list(set(testrun.requirements))
                    testrun.update()
        elif not self.use_existing_testrun:
            self.slick = SlickQA(self.url, self.project_name, self.release, self.build, self.testplan, self.testrun_name, self.environment_name, self.testrun_group)
            testrun = self.slick.testrun
            if hasattr(testrun, 'id') and self.slick.testrun.name not in self.testruns:
                self.testruns[self.testplan] = self.slick
            if self.mode == 'schedule':
                testrun.attributes = {'scheduled': 'true'}
                if self.sequential_testrun:
                    testrun.attributes['type'] = 'SEQUENTIAL'
                    testrun.state = "SCHEDULED"
                    if requirements:
                        if not hasattr(testrun, 'requirements'):
                            testrun.requirements = []
                        testrun.requirements.extend(requirements)
                        testrun.requirements = list(set(testrun.requirements))
                testrun.update()

    def get_tests(self, testsuite, data_driven=False):
        tests = []
        for test in testsuite:
            if hasattr(test, '__iter__'):
                if hasattr(test, 'test_generator') and test.test_generator is not None:
                    test.test_generator, gen = itertools.tee(test.test_generator)
                    tests.extend(self.get_tests(test, data_driven=True))
                    test.test_generator = gen
                else:
                    tests.extend(self.get_tests(test))
            else:
                if data_driven:
                    test.data_driven = True
                if self.options.slick_organize_by_tag:
                    if hasattr(testsuite.context, test.test._testMethodName):
                        method = getattr(testsuite.context, test.test._testMethodName)
                    elif test.data_driven:
                        method = testsuite.context
                    else:
                        log.error("Couldn't get tags from function.")
                        continue
                    if isinstance(self.options.slick_organize_by_tag, list):
                        test.tag = {}
                        for tag in self.options.slick_organize_by_tag:
                            if hasattr(method, tag):
                                test.tag[tag] = getattr(method, tag)
                tests.append(test)
        return tests

    def prepareTest(self, testsuite):
        if not self.enabled:
            return
        self.results = dict()
        options = self.options
        self.testplan = options.slick_testplan
        self.mode = options.slick_mode
        self.requirement_add = options.requirement_add
        self.new_requires = options.new_requires
        self.attribute_add = options.attribute_add
        self.url = options.slick_url
        self.project_name = options.slick_project_name
        self.release = options.slick_release
        self.build = options.slick_build
        self.build_function = options.slick_build_from_function
        self.testrun_name = options.slick_testrun_name
        self.environment_name = options.slick_environment_name
        self.testrun_group = options.slick_testrun_group
        self.sequential_testrun = options.sequential_testrun
        self.agent_name = options.slick_agent_name
        self.slick_duplicate = 1
        if options.slick_duplicate:
            try:
                self.slick_duplicate = int(options.slick_duplicate)
            except:
                pass
        for test in self.get_tests(testsuite):
            for i in range(self.slick_duplicate):
                assert isinstance(test, nose.case.Test)
                self.use_existing_testrun = False
                if hasattr(options, 'slick_testrun_id') and hasattr(options, 'slick_result_id') and options.slick_testrun_id is not None and options.slick_result_id is not None:
                    self.use_existing_testrun = True
                    self.testrun_id = options.slick_testrun_id
                    self.result_id = options.slick_result_id
                if self.use_existing_testrun:
                    self.slick = SlickConnection(self.url)
                    testrun = self.slick.testruns(options.slick_testrun_id).get()
                    make_testrun_updatable(testrun, self.slick)
                    result = self.slick.results(self.result_id).get()
                    make_result_updatable(result, self.slick)
                    self.results[test.id()] = result
                else:
                    testmethod = test.test._testMethodName
                    if testmethod == 'runTest' and hasattr(test.test, "test"):
                        testmethod = 'test'

                    testdata = DocStringMetaData(getattr(test.test, testmethod))
                    if not hasattr(testdata, 'automationId'):
                        testdata.automationId = test.id()
                    if not hasattr(testdata, 'automationTool'):
                        testdata.automationTool = 'python-nose'
                    if not hasattr(testdata, 'automationKey'):
                        # build key
                        address = list(test.address())
                        try:
                            if not address[0].startswith("/"):
                                testfile = os.path.relpath(address[0])
                            else:
                                testfile = address[0]
                            module_name = os.path.basename(address[0])[:-3]
                            if module_name == address[1]:
                                address.pop(1)
                            testdata.automationKey = "{0}:{1}".format(testfile, address[1])
                            if len(address) > 2:
                                try:
                                    testdata.automationKey = ".".join([testdata.automationKey, ] + address[2:])
                                except:
                                    pass
                        except:
                            pass
                    slicktest = Testcase()
                    slicktest.name = testdata.name
                    if '{' in testdata.name and '}' in testdata.name and hasattr(test.test, 'arg') and test.test.arg is not None and len(test.test.arg) > 0:
                        slicktest.name = testdata.name.format(*test.test.arg)
                    slicktest.automationId = testdata.automationId
                    slicktest.automationTool = testdata.automationTool
                    result_attributes = {}
                    requirements = None
                    if self.mode == "schedule" and self.requirement_add is not None and len(self.requirement_add) > 0:
                        for requirement_add in self.requirement_add:
                            result_attributes[requirement_add] = "required"
                            if self.new_requires:
                                if requirements is None:
                                    requirements = [requirement_add]
                                else:
                                    requirements.append(requirement_add)
                    if self.mode == "schedule" and self.attribute_add is not None and len(self.attribute_add) > 0:
                        for attribute_add in self.attribute_add:
                            key_and_value = attribute_add.split(',')
                            if len(key_and_value) == 2:
                                result_attributes[key_and_value[0]] = key_and_value[1]
                            else:
                                result_attributes[attribute_add] = 'true'
                    try:
                        actual_test_method = getattr(test.test, testmethod)
                        if hasattr(actual_test_method, REQUIRES_ATTRIBUTE):
                            requires_value = getattr(actual_test_method, REQUIRES_ATTRIBUTE)
                            if self.new_requires:
                                if requirements is None:
                                    requirements = []
                                for i in requires_value:
                                    if not isinstance(i, basestring):
                                        requirements.extend(i)
                                    else:
                                        requirements.append(i)
                            for requirement in set(requirements):
                                result_attributes[requirement] = "required"
                    except:
                        log.error("Error occurred while trying to build attributes.", exc_info=sys.exc_info)
                    if self.options.slick_organize_by_tag:
                        if hasattr(test, 'tag'):
                            self.addSlickTestrun(' - '.join(test.tag.values()), requirements=requirements)
                        else:
                            continue
                    else:
                        self.addSlickTestrun(requirements=requirements)
                    if self.mode == 'schedule':
                        result_attributes['scheduled'] = "true"
                    try:
                        #for attribute in ['automationConfiguration', 'automationKey', 'author', 'purpose', 'requirements', 'tags']:
                        #    if attribute is not None and hasattr(testdata, attribute) and getattr(testdata, attribute) is not None:
                        #        data = getattr(testdata, attribute)
                        #        if '{' in data and '}' in data and test.test.arg is not None and len(test.test.arg) > 0:
                        #            data = data.format(*test.test.arg)
                        #        setattr(slicktest, attribute, data)
                        for attribute_name, attribute_value in testdata.__dict__.items():
                            if attribute_name == 'name':
                                pass
                            elif attribute_name == 'automationId' and attribute_value == 'nose.failure.Failure.runTest':
                                setattr(slicktest, 'name', "{}: {} ({})".format(type(test.test).__name__, type(test.test.exc_val).__name__, test.test.exc_val.message))
                            elif attribute_name in slicktest._fields.keys():
                                setattr(slicktest, attribute_name, attribute_value)
                            elif attribute_name not in ('expectedResults', 'component', 'steps'):
                                result_attributes[attribute_name] = str(attribute_value)
                        if hasattr(test, 'data_driven') and test.data_driven:
                            method_file = sys.modules[getattr(test.test, testmethod).__module__].__file__
                            # Don't remove cwd because we need that
                            # if method_file.startswith(os.getcwd()):
                            #     method_file = method_file[len(os.getcwd()) + 1:]
                            if method_file.endswith('pyc'):
                                method_file = method_file[:-1]
                            if self.mode == "schedule":
                                result_attributes['snotDataDrivenModuleName'] = getattr(test.test, testmethod).__module__
                                result_attributes['snotDataDrivenFile'] = method_file
                                result_attributes['snotDataDrivenFunctionName'] = getattr(test.test, testmethod).__name__
                                result_attributes['snotDataDrivenArguments'] = pickle.dumps(test.test.arg)
                            if hasattr(test.test, 'arg') and len(test.test.arg) > 0 and isinstance(test.test.arg[-1], Requirements):
                                if requirements is None:
                                    requirements = []
                                requirements.extend(test.test.arg[-1])
                            if hasattr(getattr(test.test, testmethod), 'im_self'):
                                result_attributes['snotDataDrivenInstance'] = pickle.dumps(getattr(getattr(test.test, testmethod), 'im_self'))
                            slicktest.automationKey = "snot:data_driven_proxy"
                        slicktest.project = self.slick.project.create_reference()
                        if hasattr(testdata, 'component'):
                            comp_name = testdata.component
                            if comp_name is not None and '{' in comp_name and '}' in comp_name and hasattr(test.test, 'arg') and test.test.arg is not None and len(test.test.arg) > 0:
                                comp_name = comp_name.format(*test.test.arg)
                            component = self.slick.get_component(comp_name)
                            if component is None:
                                component = self.slick.create_component(comp_name)
                            slicktest.component = component.create_reference()
                        if hasattr(testdata, 'steps'):
                            slicktest.steps = []
                            for step in testdata.steps:
                                slickstep = Step()
                                slickstep.name = step
                                if step is not None and '{' in step and '}' in step and hasattr(test.test, 'arg') and test.test.arg is not None and len(test.test.arg) > 0:
                                    slickstep.name = step.format(*test.test.arg)
                                if hasattr(testdata, 'expectedResults') and len(testdata.expectedResults) > len(slicktest.steps):
                                    expectedResult = testdata.expectedResults[len(slicktest.steps)]
                                    slickstep.expectedResult = expectedResult
                                    if expectedResult is not None and '{' in expectedResult and '}' in expectedResult and hasattr(test.test, 'arg') and test.test.arg is not None and len(test.test.arg) > 0:
                                        slickstep.expectedResult = expectedResult.format(*test.test.arg)
                                slicktest.steps.append(slickstep)
                        if not hasattr(testdata, 'tags') and requirements:
                            slicktest.tags = list(set(requirements))
                    except:
                        log.error("Error occured when parsing for test {}:".format(test.id()), exc_info=sys.exc_info())
                    runstatus = RunStatus.TO_BE_RUN
                    if self.mode == 'schedule' and not self.sequential_testrun:
                        runstatus = RunStatus.SCHEDULED
                    if requirements is not None:
                        requirements.sort()
                    self.results[test.id()] = self.slick.file_result(slicktest.name, ResultStatus.NO_RESULT, reason="not yet run", runlength=0, testdata=slicktest, runstatus=runstatus, attributes=result_attributes, requires=requirements)
        if self.enabled and self.mode == 'schedule':
            sys.exit(0)

    def beforeTest(self, test):
        if not self.enabled:
            return
        if self.mode == 'schedule':
            raise SkipTest()

    def startTest(self, test):
        global test_failed
        test_failed = False
        if not self.enabled:
            return
        if test.id() in self.results:
            result = self.results[test.id()]
            assert isinstance(result, Result)
            if self.agent_name is not None:
                result.hostname = self.agent_name
            result.runstatus = RunStatus.RUNNING
            result.started = datetime.datetime.now()
            result.reason = ""
            if hasattr(result, 'config') and not hasattr(result.config, 'configId'):
                del result.config
            if hasattr(result, 'component') and not hasattr(result.component, 'id'):
                del result.component
            result.update()
            global current_result
            current_result = result
            if not self.options.snot_no_log_capture:
                rootLogger = logging.getLogger()
                if hasattr(self, 'loghandler') and self.loghandler is not None:
                    rootLogger.removeHandler(self.loghandler)
                self.loghandler = logging.FileHandler("/tmp/{}-testcase.log".format(result.id))
                rootLogger.setLevel(logging.DEBUG)
                self.loghandler.setFormatter(logging.Formatter("[%(asctime)s | %(levelname) 8s | %(name)s ]: %(message)s"))
                rootLogger.addHandler(self.loghandler)

    def afterTest(self, test):
        """Clear capture buffer.
        """
        if not self.enabled:
            return
        if hasattr(sys.stdout, '__class__') and hasattr(sys.stdout.__class__, '__name__') and sys.stdout.__class__.__name__ == 'StringIO':
            add_file("Nose Capture.txt", sys.stdout)
        if hasattr(self, 'loghandler') and self.loghandler is not None:
            log_filename = self.loghandler.baseFilename
            rootLogger = logging.getLogger()
            rootLogger.removeHandler(self.loghandler)
            self.loghandler.close()
            self.loghandler = None
            if os.stat(log_filename).st_size > 0:
                with open(log_filename, "r") as log_file:
                    add_file("testcase.log", log_file)
            os.unlink(log_filename)

    def addSlickResult(self, test, resultstatus=ResultStatus.PASS, err=None):
        if not self.enabled:
            return
        if self.mode == 'schedule':
            sys.exit(0)
            return
        for result_id in self.results:
            if test.id() == result_id or (len(test.config.testNames) == 1 and result_id.split(".")[-1] == test.config.testNames[0].split(".")[-1]):
                result = self.results[result_id]
                assert isinstance(result, Result)
                result.runstatus = RunStatus.FINISHED
                if resultstatus == ResultStatus.PASS and 'retry_count' in result.attributes:
                    resultstatus = ResultStatus.PASSED_ON_RETRY
                result.status = resultstatus
                result.finished = datetime.datetime.now()
                try:
                    result.runlength = int((result.finished - result.started).total_seconds() * 1000)
                except:
                    log.error("Problem trying to calculate the runlength:", exc_info=sys.exc_info())
                if on_file_result is not None:
                    try:
                        on_file_result(result)
                    except:
                        log.error("Problem calling on_file_result:", exc_info=sys.exc_info())
                if err is not None:
                    # log capture and stderr/stdout capture are appended to the message.  We don't want those showing up
                    # in the reason
                    reason_lines = None
                    if sys.version_info[0] == 2:
                        reason_lines = traceback.format_exception(*err)
                    else:
                        reason_lines = traceback.format_exception(*err, chain=not isinstance(err[1], str))
                    message_parts = reason_lines[-1].split('\n')
                    reason_lines[-1] = message_parts[0]
                    capture = None
                    if len(message_parts) > 2:
                        capture = '\n'.join(message_parts[1:])
                        reason_lines.reverse()
                    result.reason = '\n'.join(reason_lines)

                if hasattr(result, 'config') and not hasattr(result.config, 'configId'):
                    del result.config
                if hasattr(result, 'component') and not hasattr(result.component, 'id'):
                    del result.component
                result.update()
                break
        else:
            log.error("Unrecognized test %s", test.id())

    def addSuccess(self, test):
        if not self.enabled:
            return
        if self.mode == 'schedule':
            sys.exit(0)
            return
        self.addSlickResult(test)

    def addError(self, test, err):
        global test_failed
        global test_not_tested
        if not self.enabled:
            return
        if self.mode == 'schedule':
            sys.exit(0)
            return
        test_failed = True
        if err[0] is SkipTest and not test_not_tested:
            self.addSlickResult(test, ResultStatus.SKIPPED, err)
        elif err[0] is SkipTest and test_not_tested:
            self.addSlickResult(test, ResultStatus.NOT_TESTED, err)
        elif err[0] is PassedOnRetry:
            self.addSlickResult(test, ResultStatus.PASSED_ON_RETRY, err)
        else:
            self.addSlickResult(test, ResultStatus.BROKEN_TEST, err)

    def addFailure(self, test, err):
        global test_failed
        if not self.enabled:
            return
        if self.mode == 'schedule':
            sys.exit(0)
            return
        test_failed = True
        self.addSlickResult(test, ResultStatus.FAIL, err)

    def finalize(self, result):
        global testrun
        if not self.enabled or self.mode == 'schedule':
            return
        elif self.use_existing_testrun:
            testrun = self.slick.testruns(self.testrun_id).get()
            if testrun.summary.resultsByStatus.NO_RESULT == 0:
                # finish testrun
                testrun.runFinished = int(round(time.time() * 1000))
                testrun.state = RunStatus.FINISHED
                self.slick.testruns(testrun).update()
        else:
            self.slick.finish_testrun()
        return None


data_driven_parent = None
data_driven_test = None


def get_data_driven_proxy_test_objects():
    global data_driven_parent, data_driven_test
    if current_result is None:
        raise Exception("Must be using snot to run data driven proxy")
    if data_driven_parent is not None:
        return data_driven_parent, data_driven_test
    module_name = current_result.attributes["snotDataDrivenFile"].replace("/", ".")
    if "snotDataDrivenModuleName" in current_result.attributes:
        module_name = current_result.attributes["snotDataDrivenModuleName"]
    test_module = imp.load_source(module_name, current_result.attributes["snotDataDrivenFile"])
    parent = test_module
    if 'snotDataDrivenInstance' in current_result.attributes:
        parent = pickle.loads(current_result.attributes['snotDataDrivenInstance'])
    data_driven_parent = parent
    data_driven_test = getattr(parent, current_result.attributes["snotDataDrivenFunctionName"])
    return data_driven_parent, data_driven_test


def data_driven_proxy_setup():
    parent, test = get_data_driven_proxy_test_objects()
    setup_module = None
    setup_class = None
    setup_test = None
    if 'snotDataDrivenInstance' in current_result.attributes:
        # check for setupClass and setup
        for member_name, item in inspect.getmembers(parent):
            lower_case_name = member_name.lower()
            if lower_case_name == 'setupclass' or lower_case_name == 'setup_class':
                setup_class = item
            if lower_case_name == 'setup':
                setup_test = item
        # also check the module for setup_module
        for member_name, item in inspect.getmembers(inspect.getmodule(parent)):
            lower_case_name = member_name.lower()
            if lower_case_name == 'setup_module' or lower_case_name == 'setupmodule':
                setup_module = item
    if inspect.ismodule(parent):
        # check for setup_module
        for member_name, item in inspect.getmembers(parent):
            lower_case_name = member_name.lower()
            if lower_case_name == 'setup_module' or lower_case_name == 'setupmodule':
                setup_module = item
    if hasattr(test, 'setup'):
        setup_test = getattr(test, 'setup')
    setups = [setup_module, setup_class, setup_test]
    for setup in setups:
        if setup is not None and hasattr(setup, '__call__'):
            setup()


def data_driven_proxy_teardown():
    parent, test = get_data_driven_proxy_test_objects()
    teardown_module = None
    teardown_class = None
    teardown_test = None
    if 'snotDataDrivenInstance' in current_result.attributes:
        # check for teardownClass and teardown
        for member_name, item in inspect.getmembers(parent):
            lower_case_name = member_name.lower()
            if lower_case_name == 'teardownclass' or lower_case_name == 'teardown_class':
                teardown_class = item
            if lower_case_name == 'teardown':
                teardown_test = item
        # also check the module for teardown_module
        for member_name, item in inspect.getmembers(inspect.getmodule(parent)):
            lower_case_name = member_name.lower()
            if lower_case_name == 'teardown_module' or lower_case_name == 'teardownmodule':
                teardown_module = item
    if inspect.ismodule(parent):
        # check for teardown_module
        for member_name, item in inspect.getmembers(parent):
            lower_case_name = member_name.lower()
            if lower_case_name == 'teardown_module' or lower_case_name == 'teardownmodule':
                teardown_module = item
    if hasattr(test, 'teardown'):
        teardown_test = getattr(test, 'teardown')
    teardowns = [teardown_module, teardown_class, teardown_test]
    for teardown in teardowns:
        if teardown is not None and hasattr(teardown, '__call__'):
            teardown()


@nose.with_setup(data_driven_proxy_setup, data_driven_proxy_teardown)
def data_driven_proxy():
    """Data Driven Proxy Test"""
    parent, test = get_data_driven_proxy_test_objects()
    return test(*pickle.loads(current_result.attributes["snotDataDrivenArguments"]))
