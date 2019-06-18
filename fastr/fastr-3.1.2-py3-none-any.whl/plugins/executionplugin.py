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

from abc import abstractmethod
from collections import deque
import functools
import queue
import sys
import threading
import traceback
import types

from enum import Enum

import fastr
from fastr import exceptions
from fastr.abc.baseplugin import Plugin
from fastr.execution.job import Job, JobState, SourceJob, SinkJob
from fastr.helpers import iohelpers
from fastr.helpers.filesynchelper import FileSyncHelper, filesynchelper_enabled


class JobAction(Enum):
    """
    Job actions that can be performed. This is used for checking
    if held jobs should be queued, held longer or be cancelled.
    """

    hold = 'hold'
    queue = 'queue'
    cancel = 'cancel'


class ExecutionPlugin(Plugin):
    """
    This class is the base for all Plugins to execute jobs somewhere. There are
    many methods already in place for taking care of stuff.

    There are fall-backs for certain features, but if a system already
    implements those it is usually preferred to skip the fall-back and
    let the external system handle it. There are a few flags to enable
    disable these features:

    * ``cls.SUPPORTS_CANCEL`` indicates that the plugin can cancel queued jobs
    * ``cls.SUPPORTS_HOLD_RELEASE`` indicates that the plugin can queue jobs in
      a hold state and can release them again (if not, the base plugin will
      create a hidden queue for held jobs). The plugin should respect the
      ``Job.status == JobState.hold`` when queueing jobs.
    * ``cls.SUPPORTS_DEPENDENCY`` indicate that the plugin can manage job
      dependencies, if not the base plugin job dependency system will be used
      and jobs with only be submitted when all dependencies are met.
    * ``cls.CANCELS_DEPENDENCIES`` indicates that if a job is cancelled it will
      automatically cancel all jobs depending on that job. If not the plugin
      traverse the dependency graph and kill each job manual.

      .. note:: If a plugin supports dependencies it is assumed that when a
                job gets cancelled, the depending job also get cancelled
                automatically!

    Most plugins should only need to redefine a few abstract methods:

    * :py:meth:`__init__ <fastr.execution.executionpluginmanager.ExecutionPlugin.__init__>`
      the constructor
    * :py:meth:`cleanup <fastr.execution.executionpluginmanager.ExecutionPlugin.__init__>`
      a clean up function that frees resources, closes connections, etc
    * :py:meth:`_queue_job <fastr.execution.executionpluginmanager.ExecutionPlugin._queue_job>`
      the method that queues the job for execution

    Optionally an extra job finished callback could be added:

    * :py:meth:`_job_finished <fastr.execution.executionpluginmanager.ExecutionPlugin._job_finished>`
      extra callback for when a job finishes

    If ``SUPPORTS_CANCEL`` is set to True, the plugin should also implement:

    * :py:meth:`_cancel_job <fastr.execution.executionpluginmanager.ExecutionPlugin._cancel_job>`
      cancels a previously queued job

    If ``SUPPORTS_HOLD_RELEASE`` is set to True, the plugin should also implement:

    * :py:meth:`_hold_job <fastr.execution.executionpluginmanager.ExecutionPlugin._hold_job>`
      hold_job a job that is currently held
    * :py:meth:`_release_job <fastr.execution.executionpluginmanager.ExecutionPlugin._release_job>`
      releases a job that is currently held

    If ``SUPPORTED_DEPENDENCY`` is set to True, the plugin should:

        * Make sure to use the ``Job.hold_jobs`` as a list of its dependencies

    Not all of the functions need to actually do anything for a plugin. There
    are examples of plugins that do not really need a ``cleanup``, but for
    safety you need to implement it. Just using a ``pass`` for the method could
    be fine in such a case.

    .. warning::

        When overwriting other functions, extreme care must be taken not to break
        the plugins working, as there is a lot of bookkeeping that can go wrong.
    """

    #: Indicates if the plugin can cancel queued jobs
    SUPPORTS_CANCEL = False

    #: Indicates if the plugin can queue jobs in a hold state and can release
    #: them again (if not, the base plugin will create a hidden queue for held
    #: jobs)
    SUPPORTS_HOLD_RELEASE = False

    #: Indicate if the plugin can manage job dependencies, if not the base
    #: plugin job dependency system will be used and jobs with only be
    #: submitted when all dependencies are met.
    SUPPORTS_DEPENDENCY = False

    #: Indicates that when a job is cancelled the dependencies
    CANCELS_DEPENDENCIES = False

    @abstractmethod
    def __init__(self, finished_callback=None, cancelled_callback=None):
        """
        Setup the ExecutionPlugin

        :param finished_callback: the callback to call after a job finished
        :param cancelled_callback: the callback to call after a job cancelled
        :return: newly created ExecutionPlugin
        """
        super(ExecutionPlugin, self).__init__()

        # Pylint seems to be unable to figure out the .dict() member
        # pylint: disable=no-member

        self.job_status = {}
        self.job_dict = {}
        self.job_archive = {}
        self._finished_callback = finished_callback
        self._cancelled_callback = cancelled_callback

        # Dict indicating the depending jobs for a certain jobs (who is waiting on the key job id)
        self.held_queue = {}
        self.held_queue_lock = threading.Lock()

        # A list for the source jobs that should be held
        self.source_queue_lock = threading.Lock()
        self.source_job_queue = deque()
        self.queued_source_jobs = deque()
        self.source_job_limit = fastr.config.source_job_limit

        # Flag indicating the plugin is accepting new jobs queued
        self.accepting = True

        # Flag indicating the the cleanup has been performed to avoid redoing it
        self.cleaned = False

        # Create a thread for processing callbacks
        self.callback_queue = queue.Queue()
        self.processing_callbacks = True  # Flag to keep thread alive
        fastr.log.debug('Creating callback thread')
        self.callback_processor = threading.Thread(name='CallbackProcessor-0', target=self.process_callbacks, args=())
        self.callback_processor.daemon = True
        fastr.log.debug('Starting callback thread')
        self.callback_processor.start()

    def __enter__(self):
        return self

    def __exit__(self, type_, value, tb):
        self.cleanup()

    def __del__(self):
        """
        Cleanup if the variable was deleted on purpose
        """
        fastr.log.debug('Calling cleanup')
        self.cleanup()

    @abstractmethod
    def cleanup(self):
        """
        Method to call to clean up the ExecutionPlugin. This can be to clear
        temporary data, close connections, etc.

        :param force: force cleanup (e.g. kill instead of join a process)
        """
        if self.cleaned:
            return

        # Stop accepting new jobs (close the queue)
        self.accepting = False
        self.cleaned = True

        # Stop processing of callbacks
        self.processing_callbacks = False

        # Cancel all queued jobs
        while len(self.job_dict) > 0:
            job_id, job = self.job_dict.popitem()
            fastr.log.debug('Cleanup cancelling {}'.format(job_id))
            self.cancel_job(job)

        # End the callback processor
        if self.callback_processor.is_alive():
            fastr.log.debug('Terminating  callback thread')
            self.callback_processor.join()

    def register_job(self, job):
        self.job_dict[job.id] = job
        self.job_status[job.id] = job.status

        for hold_id in job.hold_jobs:
            # Add job reference to held queue to receive signal when the
            # required jobs are finished/failed. Do not subscribe for jobs that
            # are already finished.
            if hold_id in self.job_status and self.job_status[hold_id].done:
                continue

            with self.held_queue_lock:
                if hold_id not in self.held_queue:
                    self.held_queue[hold_id] = []

                self.held_queue[hold_id].append(job.id)

    def _dispatch_job(self, job):
        # Check the job requirements for dependencies and take appropriate
        # action while keeping in mind the plugin capabilities.
        action = self.check_job_requirements(job.id)
        if action == JobAction.cancel:
            self.cancel_job(job)
        elif self.SUPPORTS_DEPENDENCY or action == JobAction.queue:
            self.job_status[job.id] = job.status = JobState.queued
            self._queue_job_limited(job)
        else:  # Thus action has to be JobAction.hold:
            fastr.log.debug('Holding {} until dependencies are met'.format(job.id))
            self.job_status[job.id] = job.status = JobState.hold

            # If there is support for hold release the plugin should respect
            # the job.status being JobState.hold and it is safe to queue in
            # a held state already.
            if self.SUPPORTS_HOLD_RELEASE:
                self._queue_job_limited(job)

    def _queue_job_limited(self, job):
        # Check if it is a source job and limit if needed
        if isinstance(job, (SourceJob, SinkJob)) and self.source_job_limit > 0:
            with self.source_queue_lock:
                if len(self.queued_source_jobs) < self.source_job_limit:
                    self.queued_source_jobs.append(job.id)
                    fastr.log.debug('Queueing job, now having {} queued'.format(len(self.queued_source_jobs)))
                    self._queue_job(job)
                else:
                    # Keep the job in a temporary queue, do no dispatch!
                    fastr.log.debug('Putting soure/sink job {} in source queue due to limitations!'.format(job.id))
                    self.source_job_queue.append(job)

                    if self.SUPPORTS_HOLD_RELEASE:
                        # Submit the job in a hold state
                        fastr.log.debug('Queue SourceJob {} as hold'.format(job.status))
                        job.status = JobState.hold
                        self._queue_job(job)
        else:
            self._queue_job(job)

    def queue_job(self, job):
        """
        Add a job to the execution queue

        :param Job job: job to add
        """
        if not self.accepting:
            return

        if isinstance(job, list):
            for j in job:
                self.queue_job(j)
            return

        # Register the job for tracking
        self.register_job(job)

        # Save the job (and initial result) to file before serializing
        iohelpers.save_gpickle(job.commandfile, job)

        # If the job has been preset to done, immediately send for the callback
        if job.status in [JobState.execution_done, JobState.execution_failed]:
            self.job_finished(job)
            return

        # Dispatch the job to the plugin
        self._dispatch_job(job)

    def cancel_job(self, job):
        """
        Cancel a job previously queued

        :param job: job to cancel
        """
        if not isinstance(job, Job):
            try:
                job = self.job_dict[job]
            except KeyError:
                fastr.log.warning('Job {} is no longer under processing, cannot cancel!'.format(job))
                return

        # Make sure the job is not using a source/sink slot
        try:
            with self.source_queue_lock:
                self.source_job_queue.remove(job)
        except ValueError:
            pass  # Job was not in the source_job_queue and that is fine

        # Check if job is not already being cancelled
        if job.status == JobState.cancelled:
            # Make sure parent jobs can be freed if needed, only if still running
            if self.processing_callbacks:
                self.clean_free_jobs(job)
            job.clean()

            return

        if job.status == JobState.hold and not self.SUPPORTS_CANCEL and self.SUPPORTS_HOLD_RELEASE:
            # This is a corner case where the job is scheduled and held, but
            # somehow cannot be cancelled. We need to release the Job and let
            # it crash itself.
            self.release_job(job)

        if not self.SUPPORTS_CANCEL and job.status not in [JobState.created, JobState.hold]:
            fastr.log.warning('Job is already queued or running and cannot be cancelled anymore!')

            # Mark job as cancelled anyways to avoid revisiting
            job.status = self.job_status[job.id] = JobState.cancelled

            # Make sure parent jobs can be freed if needed, only if still running
            if self.processing_callbacks:
                self.clean_free_jobs(job)
            job.clean()

            return

        fastr.log.debug('Cancelling {}'.format(job.id))

        # Cancel job
        old_status = job.status
        job.status = self.job_status[job.id] = JobState.cancelled

        # If supported, send out the actual cancellation command
        # If the job status is created, it means it never got properly
        # accepted by the plugin and thus only needs the callback, but
        # not the actual cancellation
        if self.SUPPORTS_CANCEL and old_status != JobState.created:
            self._cancel_job(job)

        fastr.log.debug('Removing {} from jobdict'.format(job.id))
        self.job_archive[job.id] = job

        # Initialize provenance and write the final state of the job to
        # the logfile
        job.provenance.init_provenance(job)
        job.write()

        # Make sure parent jobs can be freed if needed, only if still running
        if self.processing_callbacks:
            self.clean_free_jobs(job)
        job.clean()

        try:
            del self.job_dict[job.id]
        except KeyError:
            pass

        # Calling callback for cancelling
        fastr.log.debug('Calling cancelled for {}'.format(job.id))
        if self._cancelled_callback is not None:
            self._cancelled_callback(job)

        # Cancel all children (some systems might have automatically cancelled them)
        fastr.log.debug('Cancelling children for {}'.format(job.id))

        if not self.CANCELS_DEPENDENCIES:
            if job.id in self.held_queue:
                fastr.log.debug('Found children....')
                held_queue = self.held_queue[job.id]
                for dependent_job in held_queue:
                    fastr.log.debug('Checking sub {}'.format(dependent_job))
                    if dependent_job in self.job_dict and dependent_job in self.job_status and not self.job_status[dependent_job].done:
                        fastr.log.debug('Cancelling sub {}'.format(dependent_job))
                        self.cancel_job(dependent_job)
            else:
                fastr.log.debug('No children....')

    def hold_job(self, job):
        if self.SUPPORTS_HOLD_RELEASE:
            if not isinstance(job, Job):
                if job not in self.job_dict:
                    fastr.log.warning('Job {} is no longer under processing, cannot release!'.format(job))
                    return

                try:
                    job = self.job_dict[job]
                except KeyError:
                    fastr.log.warning('Job {} is no longer under processing, cannot release!'.format(job))
                    return

            job.status = JobState.hold
            self._hold_job(job)
        else:
            raise exceptions.FastrNotImplementedError('Cannot handle hold/release by default yet!')

    def release_job(self, job):
        """
        Release a job that has been put on hold

        :param job: job to release
        """
        if not isinstance(job, Job):
            try:
                job = self.job_dict[job]
            except KeyError:
                fastr.log.warning('Job {} is no longer under processing, cannot release!'.format(job))
                return

        job.status = JobState.queued
        if self.SUPPORTS_HOLD_RELEASE:
            # Job is already queued, but held so it need to be released
            self._release_job(job)
        else:
            # Job was never queued in the first place
            self.queue_job(job)

    def job_finished(self, job, errors=None, blocking=False):
        """
        The default callback that is called when a Job finishes. This will
        create a new thread that handles the actual callback.

        :param Job job: the job that finished
        :param errors: optional list of errors encountered
        :param bool blocking: if blocking, do not create threads
        :return:
        """
        if isinstance(job, (SourceJob, SinkJob)) and self.source_job_limit > 0:
            with self.source_queue_lock:
                try:
                    self.queued_source_jobs.remove(job.id)
                except ValueError:
                    # Job is already removed
                    pass

                if len(self.source_job_queue) > 0:
                    fastr.log.debug('Taking source job from the queue')
                    new_source_job = self.source_job_queue.popleft()
                    while not new_source_job.status.idle:
                        fastr.log.warning('Discarding non-idle queued source/sink job {} ({})'.format(
                            new_source_job,
                            new_source_job.status)
                        )
                        new_source_job = self.source_job_queue.popleft()

                    fastr.log.debug('Selected {} to run'.format(new_source_job.id))
                    self.queued_source_jobs.append(new_source_job.id)
                    if self.SUPPORTS_HOLD_RELEASE:
                        self.release_job(new_source_job)
                    else:
                        self._queue_job(new_source_job)
                fastr.log.debug('New number of queued source jobs: {}'.format(
                    len(self.queued_source_jobs)
                ))

        if not blocking:
            self.callback_queue.put((job, errors))
        else:
            self._job_finished_body(job, errors)

    def process_callbacks(self):
        while self.processing_callbacks:
            try:
                job, errors = self.callback_queue.get(block=True, timeout=2)
                self._job_finished_body(job, errors)
            except queue.Empty:
                pass

        fastr.log.info('Callback processing thread for {} ended!'.format(type(self).__name__))

    def _job_finished_body(self, job, errors):
        """
        The actual callback that is executed in a separate thread. This
        method handles the collection of the result, the release of depending
        jobs and calling the user defined callback.

        :param Job job: the job that finished
        :param errors: optional list of errors encountered
        """
        fastr.log.debug('ExecutorInterface._job_finished_callback called for {}'.format(job))
        self.job_status[job.id] = JobState.processing_callback

        if errors is None:
            errors = []

        # The Job finished should always log the errors rather than
        # crashing the whole execution system
        # pylint: disable=bare-except
        try:
            try:
                if filesynchelper_enabled():
                    FileSyncHelper().wait_for_job(job.logurl)
                node = job.node
                job = iohelpers.load_gpickle(job.logfile)
                job.node = node
            except EOFError:
                errors.append(
                    exceptions.FastrResultFileNotFound(
                        job.logfile,
                        ('Could not read job result file {}, assuming '
                         'the job crashed during output write.').format(job.logfile)).excerpt())
                job.status = JobState.failed
            except IOError:
                errors.append(
                    exceptions.FastrResultFileNotFound(
                        job.logfile,
                        ('Could not find/read job result file {}, assuming '
                         'the job crashed before it created output.').format(job.logfile)).excerpt())
                job.status = JobState.failed

        except:
            exc_type, _, trace = sys.exc_info()
            exc_info = traceback.format_exc()
            trace = traceback.extract_tb(trace, 1)[0]
            fastr.log.error('Encountered exception ({}) during execution:\n{}'.format(exc_type.__name__, exc_info))
            errors.append((exc_type.__name__, exc_info, trace[0], trace[1]))
            job.status = JobState.execution_failed

        # The execution plugin found that there were errors, append them
        if len(errors) > 0:
            job.errors.extend(errors)

            # Resave the job with the updated error list
            fastr.log.info('Found errors from execution plugin, updating pickle {}'.format(job.logfile))
            iohelpers.save_gpickle(job.logfile, job)

        # Strip provenance information from the job
        del job.provenance

        result = job
        fastr.log.debug('Finished {} with status {}'.format(job.id, job.status))
        job_id = result.id

        # Make sure the status is either finished or failed
        if result.status == JobState.execution_done:
            result.status = JobState.finished
        else:
            result.status = JobState.failed

        # Set the job status so the hold jobs will be release properly
        self.job_status[job_id] = result.status
        if job_id in self.job_dict:
            self.job_dict[job_id].status = result.status

        # Do the callbacks before releasing the other jobs
        # Extra subclass callback
        fastr.log.debug('Subclass callback')
        try:
            self._job_finished(result)
        except:
            exc_type, _, _ = sys.exc_info()
            exc_info = traceback.format_exc()
            fastr.log.error('Encountered exception ({}) during callback {}._job_finished:\n{}'.format(exc_type.__name__, type(self).__name__, exc_info))

        # Extra callback from object
        fastr.log.debug('Calling callback for {}'.format(job_id))
        if self._finished_callback is not None:
            try:
                self._finished_callback(result)
            except:
                if isinstance(self._finished_callback, functools.partial):
                    args = self._finished_callback.args + tuple('{}={}'.format(k, v) for k, v in list(self._finished_callback.keywords.items()))
                    callback_name = '{f.__module__}.{f.__name__}({a})'.format(f=self._finished_callback.func, a=','.join(args))
                elif isinstance(self._finished_callback, types.FunctionType):
                    callback_name = '{f.__module__}.{f.__name__}'.format(f=self._finished_callback)
                elif isinstance(self._finished_callback, types.MethodType):
                    callback_name = '{m.__module__}.{m.__func__.__name__}'.format(m=self._finished_callback)
                else:
                    callback_name = repr(self._finished_callback)
                exc_type, _, _ = sys.exc_info()
                exc_info = traceback.format_exc()
                fastr.log.error('Encountered exception ({}) during callback {}:\n{}'.format(exc_type.__name__, callback_name, exc_info))
        else:
            fastr.log.debug('No callback specified')

        # The ProcessPoolExecutor has to track job dependencies itself, so
        # therefor we have to check for jobs depending on the finished job
        if job_id in self.held_queue:
            self.signal_dependent_jobs(job_id)

        # Clean jobs that no longer have dependencies that need to run
        self.clean_free_jobs(job)

        if isinstance(job, SinkJob):
            job.clean()

        # Move the job to archive (to keep the number of working jobs limited
        # in the future the archive can be moved to a db/disk if needed
        fastr.log.debug('Archiving job {} with status {}'.format(job_id, result.status))
        try:
            del self.job_status[job_id]
        except KeyError:
            pass

        self.job_archive[job_id] = result

        try:
            del self.job_dict[job_id]
        except KeyError:
            pass
        fastr.log.debug('Done archiving')

    def clean_free_jobs(self, job):
        for hold_job_id in job.hold_jobs:
            depending_jobs = self.held_queue.get(hold_job_id)
            if not depending_jobs:
                continue

            # Check if node of job has no undrained nodes connected to it downstream
            # This would mean that there are nodes connected which did not generate jobs
            # yet and therefore would be ignored because they are not yet part of the
            # dependency graph.
            hold_job = self.get_job(hold_job_id)
            listening_nodes = [x.target.node for x in hold_job.node.listeners]
            if not all(x.drained for x in listening_nodes):
                fastr.log.debug('Not all listening nodes are drained of jobs, cannot clean up yet')
                continue
            else:
                fastr.log.debug('All listeners are drained, we can safely clean up')

            # Check if all depending jobs are done
            if all(self.get_status(x).done for x in depending_jobs):
                with self.held_queue_lock:
                    del self.held_queue[hold_job_id]

                job_to_clean = self.get_job(hold_job_id)
                job_to_clean.clean()

    def get_job(self, job_id):
        try:
            return self.job_dict[job_id]
        except KeyError:
            try:
                return self.job_archive[job_id]
            except:
                raise exceptions.FastrKeyError('Could not find job {}'.format(job_id))

    def get_status(self, job):
        if not isinstance(job, Job):
            job = self.get_job(job)

        return job.status

    @abstractmethod
    def _queue_job(self, job):
        """
        Method that a subclass implements to actually queue a Job for execution

        :param job: job to queue

        .. note:: If ``SUPPORT_HOLD_RELEASE=True`` the plugin should check
                  ``job.status`` to see if it is ``JobStatus.hold``. If
                  this is the case it should submit the job in a held
                  state to be released at a later time. If
                  ``SUPPORT_HOLD_RELEASE=False`` the status be ignored.
        """

    def _cancel_job(self, job):
        """
        Method that a subclass implements to actually cancel a Job

        :param job: job to cancel
        """
        if self.SUPPORTS_CANCEL:
            raise exceptions.FastrPluginCapabilityNotImplemented('The plugin should have reimplemented _cancel_job!')
        else:
            fastr.log.warning('Cannot remove job {} from a {} queue!'.format(job.id,
                                                                             type(self).__name__))

    def _hold_job(self, job):
        """
        Method that a subclass implements to hold a queued/running Job, only
        required if ``SUPPORT_HOLD_RELEASE=True``

        :param job: Job to hold
        """
        if self.SUPPORTS_HOLD_RELEASE:
            raise exceptions.FastrPluginCapabilityNotImplemented(
                'Cannot hold job {}: the plugin should have reimplemented _hold_job!'.format(
                    job.id
                )
            )

    def _release_job(self, job):
        """
        Method that a subclass implements to actually release a job, only
        required if ``SUPPORT_HOLD_RELEASE=True``

        :param job: job to release from hold
        """
        if self.SUPPORTS_HOLD_RELEASE:
            raise exceptions.FastrPluginCapabilityNotImplemented(
                'Cannot release job {}: the plugin should have reimplemented _release_job!'.format(
                    job.id
                )
            )

    def _job_finished(self, job):
        """
        Method that a subclass can implement to add to the default callback.
        It will be called by ``_job_finished_body`` right before the user
        defined callback will be called.

        :param job: Job that resulted from the execution
        """

    def show_jobs(self, req_status=None):
        """
        List the queued jobs, possible filtered by status

        :param req_status: requested status to filter on
        :return: list of jobs
        """
        if isinstance(req_status, str):
            req_status = JobState[req_status]

        if not isinstance(req_status, JobState):
            return []

        results = []
        for key, status in self.job_status.items():
            if req_status is None or status == req_status:
                results.append(self.get_job(key))

        return results

    def check_job_status(self, job_id):
        """
        Get the status of a specified job

        :param job_id: the target job
        :return: the status of the job (or None if job not found)
        """
        try:
            return self.get_status(job_id)
        except exceptions.FastrKeyError:
            return None

    def check_job_requirements(self, job_id):
        """
        Check if the requirements for a job are fulfilled.

        :param job_id: job to check
        :return: directive what should happen with the job
        :rtype: JobAction
        """
        job = self.get_job(job_id)
        if job.hold_jobs is None or len(job.hold_jobs) == 0:
            return JobAction.queue

        status_list = [self.check_job_status(jid) for jid in job.hold_jobs]

        if all(x.done for x in status_list):
            if all(x == JobState.finished for x in status_list):
                return JobAction.queue
            else:
                return JobAction.cancel
        else:
            return JobAction.hold

    def signal_dependent_jobs(self, job_id):
        """
        Check all depedent jobs and process them if all their dependencies are met.
        :param job_id:
        :return:
        """
        fastr.log.debug('Signaling depending jobs {}'.format(self.held_queue[job_id]))
        ready_jobs = []
        for held_job_id in self.held_queue[job_id]:
            action = self.check_job_requirements(held_job_id)
            if action == JobAction.queue:
                # If ready, flag job for removal from held queue and send
                # to pool queue to be executed
                fastr.log.debug('Job {} is now ready to be submitted'.format(held_job_id))
                ready_jobs.append(held_job_id)
                if not self.SUPPORTS_DEPENDENCY:
                    self.release_job(held_job_id)
            elif action == JobAction.cancel:
                fastr.log.debug('Job {} will be cancelled'.format(held_job_id))
                ready_jobs.append(held_job_id)
                self.cancel_job(held_job_id)
            else:
                fastr.log.debug('Job {} still has unmet dependencies'.format(held_job_id))

        return tuple(ready_jobs)
