import os

from pyats.log import managed_handlers

import logging

logger = logging.getLogger(__name__)

RESULT_MAP = {
    'PASS': 'passed',
    'FAIL': 'failed',
    'NOT_RUN': 'skipped',
}

class AEReportListener(object):
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, client,
                       runinfo_dir,
                       task_id,
                       task_args):
        self.client = client
        self.runinfo_dir = runinfo_dir
        self.task_id = task_id
        self.task_args = task_args

        self.in_test = False

        # rig the logging system so start/end messages only show in tasklog
        logger.handlers.append(managed_handlers.tasklog)
        logger.propagate = False

    @property
    def logfile(self):
        return managed_handlers.tasklog.logfile

    def start_suite(self, name, attributes):
        # flush log
        managed_handlers.tasklog.flush()

        self.client.start_testscript(logfilepath = self.logfile,
                                     logging = 'filepertestcase',
                                     taskid = self.task_id)

        self.script = os.path.basename(attributes['source']).split('.')[0]

        self.client.set_initinfo(script = {'name': attributes['longname'],
                                           'path': attributes['source'],
                                           'version': 'unknown',
                                           'description': attributes['doc']},

                                 pargs = str(self.task_args),
                                 logfile = {'file_path': self.logfile})

    def end_suite(self, name, attributes):
        # flush log
        managed_handlers.tasklog.flush()

        self.client.stop_testscript()

    def start_test(self, name, attributes):
        logger.info("Starting testcase '%s'" % name)

        self.in_test = True
        # flush log
        managed_handlers.tasklog.flush()

        module, tc_name = attributes['longname'].split('.')
        attributes['module'] = self.script

        # start tc
        self.client.start_testcase(tcid= tc_name,
                                   logfilepath = self.logfile,
                                   name = tc_name,
                                   extra = attributes,
                                   description = attributes['doc'])

    def end_test(self, name, attributes):
        result = RESULT_MAP[attributes['status']]

        logger.info("The result of testcase '%s' is => %s" % (name,
                                                              result.upper()))
        self.in_test = False

        # flush log
        managed_handlers.tasklog.flush()

        # stop tc
        self.client.stop_testcase(result = {'mode':'auto',
                                            'value': result})

    def start_keyword(self, name, attributes):
        if not self.in_test:
            return

        logger.info("Starting section '%s'" % name)

        # flush log
        managed_handlers.tasklog.flush()

        # start section
        self.client.start_testsection(sectionid = attributes['kwname'],
                                      name = attributes['kwname'],
                                      logfilepath = self.logfile,
                                      extra = attributes,
                                      description = attributes['doc'])

    def end_keyword(self, name, attributes):
        if not self.in_test:
            return

        result = RESULT_MAP[attributes['status']]
        logger.info("The result of section '%s' is => %s" % (name,
                                                             result.upper()))

        # flush log
        managed_handlers.tasklog.flush()

        # report it
        self.client.stop_testsection(result = {'mode':'auto',
                                               'value': result})
