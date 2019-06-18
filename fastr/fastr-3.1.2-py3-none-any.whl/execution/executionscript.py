#!/usr/bin/python

# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The executionscript is the script that wraps around a tool executable. It
takes a job, builds the command, executes the command (while profiling it)
and collects the results.
"""

import datetime
import os
import sys
import traceback

print('=== Loading Fastr execution script  ===')
print('Using python {} loaded from {}'.format(sys.version, sys.executable))

FASTR_LOG_TYPE = 'console'
import fastr
from fastr import exceptions
from fastr.execution.job import Job, JobState
from fastr.helpers.filesynchelper import FileSyncHelper, filesynchelper_enabled
from fastr.helpers.iohelpers import load_gpickle
from fastr.helpers.sysinfo import get_hostinfo, get_sysinfo
from fastr.resources import ioplugins

_MONITOR_INTERVAL = 1.0

# We will run untrusted subprocesses and want to log everything also in case
# of an error. Therefor there are a few bare-except blocks which are intended
# to ensure as much as possible logging in case of errors.
# pyline: disable=bare-except


def execute_job(job):
    """
    Execute a Job and save the result to disk

    :param job: the job to execute
    """
    fastr.log.info('Using Python {}'.format(sys.version))
    fastr.log.info('FASTR loaded from {}'.format(fastr.__file__))
    fastr.log.info('version: {}'.format(fastr.version.full_version))
    fastr.log.info('Start time: {}'.format(datetime.datetime.now()))

    logfile_path = job.logfile
    fastr.log.info('Job log path: {}'.format(logfile_path))

    fastr.log.info('Running job {}\n  command: {} v{}\n  arguments: {}\n  outputs: {}\n'.format(job.id, job.tool_name, job.tool_version, job.input_arguments, job.output_arguments))
    try:
        # Checking for old results of a job run before continuing
        old_job_result = job.get_result()

        if old_job_result is not None:
            fastr.log.info('Found a valid job results, re-using that as output')
            job = old_job_result

        else:
            fastr.log.info('No old result, executing job')
            job.status = JobState.running

            # Initialize provenance
            job.provenance.init_provenance(job)

            job.info_store['hostinfo'] = get_hostinfo()
            job.info_store['sysinfo_start'] = get_sysinfo()

            fastr.log.info('DRMAA info: {}'.format(job.info_store['hostinfo']['drmaa']))

            fastr.log.info('Writing intermediate job info to: {}'.format(logfile_path))
            job.write()

            job.execute()

            # Document system information after
            fastr.log.info('Job subprocess finished')
            job.info_store['sysinfo_end'] = get_sysinfo()

            fastr.log.info('Start hashing results')
            start = datetime.datetime.now()
            job.hash_results()
            end = datetime.datetime.now()
            fastr.log.info('Finished hashing results in {} seconds'.format((end - start).total_seconds()))
            fastr.log.info('try end time: {}'.format(datetime.datetime.now()))
    except BaseException as exception:
        fastr.log.warning('Caught exception in execution: [{}] {}'.format(type(exception).__name__,
                                                                          exception))
        job.status = JobState.execution_failed
        traceback.print_exc()

        # Log errors to the info store
        if 'process' not in job.info_store:
            job.errors.append(exceptions.FastrSubprocessNotFinished('There is no information that the subprocess finished properly: appears the job crashed before the subprocess registered as finished.').excerpt())
        elif job.info_store['process']['stderr'] != '':
            job.errors.append(exceptions.FastrErrorInSubprocess(job.info_store['process']['stderr']).excerpt())

        # Add exception as error in job
        exc_type, exception, trace = sys.exc_info()
        exc_info = traceback.format_exc()
        if isinstance(exception, exceptions.FastrError):
            job.errors.append(exception.excerpt())
        else:
            trace = traceback.extract_tb(trace, 1)[0]
            job.errors.append((exc_type.__name__, exception.message, trace[0], trace[1]))
        fastr.log.critical('Execution script encountered errors: {}'.format(exc_info))
    else:
        fastr.log.info('Execution finished normally.')
        job.status = JobState.execution_done
    finally:
        fastr.log.info('Writing job result to: {}'.format(logfile_path))
        job.write()

        # Cleanup all plugins
        ioplugins.cleanup()

        if filesynchelper_enabled():
            FileSyncHelper().job_finished(job.logurl)

        fastr.log.info('End time: {}'.format(datetime.datetime.now()))

        if job.status != JobState.execution_done:
            sys.exit(1)  # Signal that the job failed


def main(joblist=None):
    """
    This is the main code. Wrapped inside a function to avoid the variables
    being seen as globals and to shut up pylint. Also if the joblist argument
    is given it can run any given job, otherwise it takes the first command
    line argument.
    """
    fastr.log.info('----- Execution script -----\n')
    if joblist is None:
        joblist = sys.argv[1]
        if filesynchelper_enabled():
            # we are using file promises
            # running this execution script with a path to
            # a pickle is a promise in itself so we should
            # wait until jobfile exists or timeout occurs
            file_sync_helper = FileSyncHelper()
            file_sync_helper.wait_for_pickle(joblist)

    if os.path.exists(joblist) and os.path.isfile(joblist):
        fastr.log.info('Loading pickled command from file')
        start = datetime.datetime.now()
        joblist = load_gpickle(joblist)
        end = datetime.datetime.now()
        fastr.log.info('Finished loading pickle in {} seconds'.format((end - start).total_seconds()))

    # Both the error we raise and not able to iterate joblist will result in a
    # TypeError, so we catch both and give our own TypeError message
    try:
        if not isinstance(joblist, Job) and not all(isinstance(x, Job) for x in joblist):
            raise TypeError('Wrong type, found {}!'.format(type(joblist)))
    except TypeError:
        message = 'Argument should be a Job or a iterable of Jobs! (Found: {})'.format(joblist)
        fastr.log.critical(message)
        raise exceptions.FastrTypeError(message)

    fastr.log.info('Received command: {command}\n'.format(command=joblist))

    if isinstance(joblist, list) or isinstance(joblist, tuple):
        for job in joblist:
            execute_job(job)
    elif isinstance(joblist, Job):
        execute_job(joblist)
    fastr.log.info('---------------------------\n')


if __name__ == '__main__':
    main()
