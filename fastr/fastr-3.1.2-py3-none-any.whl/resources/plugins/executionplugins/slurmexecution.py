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

import json
import os
import re
import shlex
import subprocess
import sys
import threading
import time

import fastr
from fastr import exceptions
from fastr.plugins.executionplugin import ExecutionPlugin
from fastr.execution.job import JobState
from fastr.helpers.classproperty import classproperty

SBATCH_SCRIPT_TEMPLATE = \
"""#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task {cores}
{memory}
{time}
{partition}
#SBATCH --output {stdout}
#SBATCH --error {stderr}
{depends}
{hold}

{command}
"""


class SlurmExecution(ExecutionPlugin):
    """
    """

    SQUEUE_FORMAT = '{"id": %.18i, "status": "%.2t"}'

    # Job state, compact form:
    #   PD (pending),
    #    R (running),
    #   CA (cancelled),
    #   CF(configuring),
    #   CG (completing),
    #   CD (completed),
    #    F (failed),
    #   TO (timeout),
    #   NF (node failure),
    #   RV (revoked) and
    #   SE (special exit state).
    STATUS_MAPPING = {
        'PD': JobState.queued,
        ' R': JobState.running,
        'CA': JobState.cancelled,
        'CF': JobState.running,
        'CG': JobState.running,
        'CD': JobState.finished,
        ' F': JobState.failed,
        'TO': JobState.queued,
        'NF': JobState.failed,
        'RV': JobState.cancelled,
        'SE': JobState.failed,
    }

    # SLURM COMMANDS
    SBATCH = 'sbatch'
    SCANCEL = 'scancel'
    SQUEUE = 'squeue'
    SCONTROL = 'scontrol'

    # Advertise capabilities
    SUPPORTS_DEPENDENCY = True
    SUPPORTS_CANCEL = True
    SUPPORTS_HOLD_RELEASE = True

    def __init__(self, finished_callback=None, cancelled_callback=None):
        super(SlurmExecution, self).__init__(finished_callback, cancelled_callback)

        # Config value
        self.check_interval = fastr.config.slurm_job_check_interval
        self.partition = fastr.config.slurm_partition

        # Make it possible to run self-terminating threads
        self.running = True

        # Create job translation table
        self.job_translation_table = dict()
        self.job_lookup_table = dict()

        # Start job status checker
        fastr.log.debug('Creating job status checker')
        self.job_checker = threading.Thread(name='SlurmJobChecker-0', target=self.job_status_check, args=())
        self.job_checker.daemon = True
        fastr.log.debug('Starting job status checker')
        self.job_checker.start()

    @classproperty
    def configuration_fields(cls):
        return {
            "slurm_job_check_interval": (int, 30, "The interval in which the job checker will start"
                                                  "to check for stale jobs"),
            "slurm_partition": (str, '', "The slurm partition to use")
        }

    @classmethod
    def test(cls):
        # Check if requirement commands can be called
        try:
            subprocess.check_output([cls.SBATCH, '--help'], stderr=subprocess.STDOUT)
        except OSError:
            raise exceptions.FastrExecutableNotFoundError(cls.SBATCH)

        try:
            subprocess.check_output([cls.SQUEUE, '--help'], stderr=subprocess.STDOUT)
        except OSError:
            raise exceptions.FastrExecutableNotFoundError(cls.SQUEUE)

        try:
            subprocess.check_output([cls.SCONTROL, '--help'], stderr=subprocess.STDOUT)
        except OSError:
            raise exceptions.FastrExecutableNotFoundError(cls.SCONTROL)

        try:
            subprocess.check_output([cls.SCANCEL, '--help'], stderr=subprocess.STDOUT)
        except OSError:
            raise exceptions.FastrExecutableNotFoundError(cls.SCANCEL)

    def cleanup(self):
        self.running = False
        super(SlurmExecution, self).cleanup()

    def _job_finished(self, result):
        pass

    def _queue_job(self, job):
        # Encode command to execute
        command = [sys.executable,
                   os.path.join(fastr.config.executionscript),
                   job.commandfile]
        command = ' '.join(shlex.quote(item) for item in command)

        # Encode job dependencies
        depends = ''
        if job.hold_jobs:
            depend_jobs = [self.job_lookup_table.get(j, None) for j in job.hold_jobs]
            depend_jobs = [str(x) for x in depend_jobs if x is not None]
            if depend_jobs:
                depends = '#SBATCH --dependency=afterok:{}'.format(','.join(depend_jobs))

        if job.required_memory:
            required_memory = '#SBATCH --mem {}M'.format(job.required_memory)
        else:
            required_memory = ''

        if job.required_time:
            required_time = '#SBATCH --time {}'.format(job.required_time)
        else:
            required_time = ''

        if self.partition:
            partition = '#SBATCH --partition {}'.format(self.partition)
        else:
            partition = ''

        # Check if the job is ready to run or must be held
        if job.status == JobState.hold:
            hold = '--hold'
        else:
            hold = ''

        # Create SBATCH script from template
        sbatch_script = SBATCH_SCRIPT_TEMPLATE.format(
            cores=job.required_cores or 1,
            memory=required_memory,
            time=required_time,
            partition=partition,
            stdout=job.stdoutfile,
            stderr=job.stderrfile,
            command=command,
            depends=depends,
            hold=hold,
        )

        if fastr.config.debug:
            fastr.log.debug('USING SBATCH SCRIPT:\n{}'.format(sbatch_script))

        sbatch = subprocess.Popen(
            [self.SBATCH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Feed script via stdin and get result
        stdout, stderr = sbatch.communicate(sbatch_script)

        match = re.search(r'Submitted batch job (\d+)', stdout)

        if match:
            cl_job_id = int(match.group(1))
        else:
            # Set errors and process job as failed
            fastr.log.error('Could not submit job, sbatch returned:\n{}\n{}'.format(stdout, stderr))
            job.status = JobState.execution_failed
            self.job_finished(job, errors=["FastrSlurmSubmitError",
                                           stderr,
                                           __file__,
                                           "unknown"])
            return

        self.job_translation_table[cl_job_id] = job
        self.job_lookup_table[job.id] = cl_job_id

    def _cancel_job(self, job):
        """
        Cancel a given job

        :param job:
        """
        try:
            slurm_job_id = self.job_lookup_table.pop(job.id)
        except KeyError:
            fastr.log.info('Job {} not found in SLURM lookup'.format(job.id))
            return

        scancel_process = subprocess.Popen([self.SCANCEL, str(slurm_job_id)])
        stdout, stderr = scancel_process.communicate()

        if stderr:
            fastr.log.warning('Encountered error when cancelling job: {}'.format(job.id))

        try:
            del self.job_translation_table[slurm_job_id]
        except KeyError:
            pass  # This job is already gone

    def _hold_job(self, job):
        slurm_job_id = self.job_lookup_table.get(job.id, None)
        if slurm_job_id:
            scontrol_process = subprocess.Popen([self.SCONTROL, "hold", str(slurm_job_id)])
            stdout, stderr = scontrol_process.communicate()
            if stderr:
                fastr.log.warning('Encountered error when holding job: {}'.format(job.id))
        else:
            fastr.log.error('Cannot hold job {}, cannot find the slurm id!'.format(job.id))

    def _release_job(self, job):
        slurm_job_id = self.job_lookup_table.get(job.id, None)
        if slurm_job_id:
            scontrol_process = subprocess.Popen([self.SCONTROL, "release", str(slurm_job_id)])
            stdout, stderr = scontrol_process.communicate()
            if stderr:
                fastr.log.warning('Encountered error when releasing job: {}'.format(job.id))
        else:
            fastr.log.error('Cannot release job {}, cannot find the slurm id!'.format(job.id))

    def job_status_check(self):
        last_update = time.time()

        while self.running:
            if time.time() - last_update < self.check_interval:
                time.sleep(1)
                continue

            fastr.log.debug('Running job status check')
            last_update = time.time()  # Reset timer
            cluster_job_ids = set(self.job_lookup_table.values() + self.job_translation_table.keys())

            command = [self.SQUEUE,
                       '-o', self.SQUEUE_FORMAT,
                       '-j', ','.join(str(x) for x in cluster_job_ids)]

            squeue = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = squeue.communicate()

            job_info = {}
            for line in stdout.splitlines()[1:]:
                if line.strip() == '':
                    continue
                job = json.loads(line)
                job_info[job['id']] = job['status']

            for job_id in cluster_job_ids:
                if job_id not in job_info:
                    # Job is done, remove from plugin tracking and dispatch callbacks
                    job = self.job_translation_table.pop(job_id, None)

                    if job is not None:
                        # Send the result to the callback function
                        try:
                            del self.job_lookup_table[job.id]
                        except KeyError:
                            fastr.log.warning('Found an inconsistency in the job_lookup_table,'
                                              ' cannot find job to remove')

                    self.job_finished(job)
                else:
                    # Update the job status
                    job = self.job_translation_table[job_id]
                    status = self.STATUS_MAPPING.get(job_info[job_id], None)

                    if status is None:
                        fastr.log.info('Found a job with unknown state: {}'.format(job_info[job_id]))
                        continue

                    job.status = status
