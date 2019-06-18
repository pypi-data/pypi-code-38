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
from queue import Queue, Empty
import subprocess
import sys
from threading import Thread
import traceback

import fastr
from fastr.plugins.executionplugin import ExecutionPlugin
from fastr.execution.job import JobState


class LinearExecution(ExecutionPlugin):
    """
    An execution engine that has a background thread that executes the jobs in
    order. The queue is a simple FIFO queue and there is one worker thread that
    operates in the background. This plugin is meant as a fallback when other
    plugins do not function properly. It does not multi-processing so it is
    safe to use in environments that do no support that.
    """
    def __init__(self, finished_callback=None, cancelled_callback=None):
        super(LinearExecution, self).__init__(finished_callback, cancelled_callback)
        self.job_queue = Queue()
        self.timeout = 1.0
        self._exec_thread = Thread(None, self.exec_worker, 'ExecWorker')
        self.running = True
        self._exec_thread.start()

    @classmethod
    def test(cls):
        pass  # No need to test stuff

    def _queue_job(self, job):
        # Check if the job is ready to run or must be held
        fastr.log.debug('Queueing {}'.format(job.id))
        self.job_queue.put(job)

    def _job_finished(self, result):
        pass

    def cleanup(self):
        super(LinearExecution, self).cleanup()
        self.running = False
        self._exec_thread.join()
        self.job_status.clear()

    def exec_worker(self):
        while self.running:
            try:
                job = self.job_queue.get(True, self.timeout)

                # Make sure subprocess causes no trouble
                try:
                    fastr.log.debug('Running job {}'.format(job.id))
                    job.status = JobState.running

                    command = [sys.executable,
                               os.path.join(fastr.config.executionscript),
                               job.commandfile]

                    with open(job.stdoutfile, 'a') as fh_stdout, open(job.stderrfile, 'a') as fh_stderr:
                        proc = subprocess.Popen(command, stdout=fh_stdout, stderr=fh_stderr)
                        proc.wait()

                        fastr.log.debug('Subprocess finished')
                    fastr.log.debug('Finished {}'.format(job.id))
                except Exception:
                    exc_type, _, trace = sys.exc_info()
                    exc_info = traceback.format_exc()
                    trace = traceback.extract_tb(trace, 1)[0]
                    fastr.log.error('Encountered exception ({}) during execution:\n{}'.format(exc_type.__name__, exc_info))
                    job.info_store['errors'].append((exc_type.__name__, exc_info, trace[0], trace[1]))
                finally:
                    self.job_finished(job)
                    self.job_queue.task_done()

            except Empty:
                pass
