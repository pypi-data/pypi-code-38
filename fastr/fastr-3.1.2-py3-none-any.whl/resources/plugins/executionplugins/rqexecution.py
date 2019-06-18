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

import os
import subprocess
import sys
import threading
import time
import traceback

import fastr
import fastr.resources
from fastr.abc.baseplugin import PluginState
from fastr.plugins.executionplugin import ExecutionPlugin
from fastr.helpers.classproperty import classproperty

try:
    from rq import Queue
    from redis import Redis
    IMPORT_SUCCESS = True
except ImportError:
    IMPORT_SUCCESS = False


class RQExecution(ExecutionPlugin):
    """
    A execution plugin based on Redis Queue. Fastr will submit jobs to the
    redis queue and workers will peel the jobs from the queue and process
    them.

    This system requires a running redis database and the database url has to
    be set in the fastr configuration.

    .. note::

        This execution plugin required the ``redis`` and ``rq`` packages to
        be installed before it can be loaded properly.
    """
    if not IMPORT_SUCCESS:
        _status = (PluginState.failed, 'Could not load rq and/or redis!')

    def __init__(self, finished_callback=None, cancelled_callback=None):
        super(RQExecution, self).__init__(finished_callback, cancelled_callback)
        redis = Redis.from_url(fastr.config.rq_host)
        self.queue = Queue(name=fastr.config.rq_queue, connection=redis, default_timeout=-1)
        self.rq_jobs = {}
        self.running = True

        fastr.log.debug('Creating rq job collector')
        self.collector = threading.Thread(name='RQJobCollector-0', target=self.check_finished, args=())
        self.collector.daemon = True
        fastr.log.debug('Starting rq job collector')
        self.collector.start()

    @classmethod
    def test(cls):
        if not IMPORT_SUCCESS:
            raise ImportError('Cannot import required modules (rq and redis are required)')

    @classproperty
    def configuration_fields(cls):
        return {
            "rq_host": (str, "redis://localhost:6379/0", "The url of the redis serving the redis queue"),
            "rq_queue": (str, "default", "The redis queue to use"),
        }

    def cleanup(self):
        super(RQExecution, self).cleanup()

    def _job_finished(self, result):
        pass

    def _cancel_job(self, job):
        pass

    def _queue_job(self, job):
        # Check if the job is ready to run or must be held
        rq_job = self.queue.enqueue(self.run_job,
                                    job.id,
                                    job.commandfile,
                                    job.stdoutfile,
                                    job.stderrfile,
                                    job_id=job.id,
                                    ttl=-1)
        self.rq_jobs[job.id] = rq_job

    def check_finished(self):
        while self.running:
            for job_id, rq_job in self.rq_jobs.items():
                # Check if job is finished
                if rq_job.is_finished or rq_job.is_failed:
                    job = self.job_dict[job_id]
                    self.job_finished(job)
                    del self.rq_jobs[job_id]

            time.sleep(1.0)

    @classmethod
    def run_job(cls, job_id, job_command, job_stdout, job_stderr):
        try:
            fastr.log.debug('Running job {}'.format(job_id))

            command = [sys.executable,
                       os.path.join(fastr.config.executionscript),
                       job_command]

            with open(job_stdout, 'w') as fh_stdout, open(job_stderr, 'w') as fh_stderr:
                proc = subprocess.Popen(command, stdout=fh_stdout, stderr=fh_stderr)
                proc.wait()
                fastr.log.debug('Subprocess finished')
            fastr.log.debug('Finished {}'.format(job_id))
        except Exception:
            exc_type, _, trace = sys.exc_info()
            exc_info = traceback.format_exc()
            fastr.log.error('Encountered exception ({}) during execution:\n{}'.format(exc_type.__name__, exc_info))
            raise
