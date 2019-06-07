import inspect
import json
import logging
import os
import sys
import tempfile
import time
import uuid

from alv3_service.common import identify
from alv3_service.common import log, mock_forge
from alv3_service.common.result import Result
from alv3_service.common.result import ResultSection
from alv3_service.common.task import Task
from assemblyline.common import digests
from assemblyline.common import exceptions
from assemblyline.common import net
from assemblyline.common import version

Classification = mock_forge.get_classification()


class UpdaterFrequency(object):
    MINUTE = 60
    QUARTER_HOUR = MINUTE * 15
    HALF_HOUR = MINUTE * 30
    HOUR = MINUTE * 60
    QUAD_HOUR = HOUR * 4
    QUARTER_DAY = HOUR * 6
    HALF_DAY = HOUR * 12
    DAY = HOUR * 24

    @staticmethod
    def is_valid(freq):
        try:
            int(freq)
        except ValueError:
            return False

        return freq >= UpdaterFrequency.MINUTE


class UpdaterType(object):
    BOX = 'box'
    CLUSTER = 'cluster'
    PROCESS = 'process'
    NON_BLOCKING = 'non_blocking'

    @staticmethod
    def is_valid(utype):
        return utype in [UpdaterType.BOX, UpdaterType.CLUSTER, UpdaterType.PROCESS, UpdaterType.NON_BLOCKING]

    @staticmethod
    def blocking_types():
        return [
            UpdaterType.BOX,
            UpdaterType.CLUSTER,
            UpdaterType.PROCESS
        ]

    @staticmethod
    def unique_updater_types():
        return [
            UpdaterType.BOX,
            UpdaterType.CLUSTER
        ]


class ServiceBase(object):

    # If a service indicates it is a BATCH_SERVICE, the driver will attempt to
    # spool multiple requests before invoking the services execute() method.
    BATCH_SERVICE = False

    SERVICE_ACCEPTS = '.*'
    SERVICE_REJECTS = 'empty|metadata/.*'

    SERVICE_CATEGORY = 'Uncategorized'
    SERVICE_CLASSIFICATION = Classification.UNRESTRICTED
    # The default cfg used when an instance of this service is created.
    # Override this in your subclass with sane defaults for your service.
    # Default service config is a key/value where the value can be str, bool, int or list. Nothing else
    SERVICE_DEFAULT_CONFIG = {}
    # The default submission parameters that will be made available to the users when they submit files to your service.
    # Override this in your subclass with sane defaults for your service.
    # Default submission params list of dictionary. Dictionaries must have 4 keys (default, name, type, value) where
    # default is the default value, name is the name of the variable, type is the type of data (str, bool, int or list)
    #  and value should be set to the same as default.
    SERVICE_DEFAULT_SUBMISSION_PARAMS = []
    SERVICE_DESCRIPTION = "N/A"
    SERVICE_DISABLE_CACHE = False
    SERVICE_ENABLED = False
    SERVICE_FILE_REQUIRED = True
    SERVICE_LICENCE_COUNT = 0
    SERVICE_REVISION = '0'
    SERVICE_SAVE_RESULT = True
    SERVICE_SAFE_START = False
    SERVICE_STAGE = 'CORE'
    SERVICE_SUPPORTED_PLATFORMS = ['Linux']
    SERVICE_TIMEOUT = 60
    SERVICE_VERSION = '0'
    SERVICE_IS_EXTERNAL = False

    SERVICE_CPU_CORES = 1
    SERVICE_RAM_MB = 1024

    def __init__(self, cfg=None):
        # Start with default config and override that with anything provided.
        self.cfg = self.SERVICE_DEFAULT_CONFIG.copy()
        if cfg:
            self.cfg.update(cfg)

        log.init_logging(log_level=logging.INFO)

        # Initialize non trivial members in start_service rather than __init__.
        self.log = logging.getLogger('assemblyline.svc.{}'.format(self.service_name().lower()))
        self.dispatch_queue = None
        self.result_store = None
        self.submit_client = None
        self.transport = None
        self.worker = None
        self._working_directory = None
        self._ip = '127.0.0.1'
        self.mac = net.get_mac_for_ip(net.get_hostip())
        self._updater = None
        self._updater_id = None
        self.submission_tags = {}

    def start(self):
        """
        Called at worker start.

        :return:
        """
        pass

    def stop(self):
        pass

    @classmethod
    def service_name(cls):
        return cls.__name__

    def get_tool_version(self):
        return ''

    @classmethod
    def get_default_config(cls):
        return {
            'BATCH_SERVICE': cls.BATCH_SERVICE,
            'SERVICE_ACCEPTS': cls.SERVICE_ACCEPTS,
            'SERVICE_CATEGORY': cls.SERVICE_CATEGORY,
            'SERVICE_CLASSPATH': '.'.join((cls.__module__, cls.service_name())),
            'SERVICE_CPU_CORES': cls.SERVICE_CPU_CORES,
            'SERVICE_DEFAULT_CONFIG': cls.SERVICE_DEFAULT_CONFIG,
            'SERVICE_DEFAULT_SUBMISSION_PARAMS': cls.SERVICE_DEFAULT_SUBMISSION_PARAMS,
            'SERVICE_DESCRIPTION': cls.SERVICE_DESCRIPTION,
            'SERVICE_ENABLED': cls.SERVICE_ENABLED,
            'SERVICE_FILE_REQUIRED': cls.SERVICE_FILE_REQUIRED,
            'SERVICE_IS_EXTERNAL': cls.SERVICE_IS_EXTERNAL,
            'SERVICE_LICENCE_COUNT': cls.SERVICE_LICENCE_COUNT,
            'SERVICE_NAME': cls.service_name(),
            'SERVICE_RAM_MB': cls.SERVICE_RAM_MB,
            'SERVICE_REJECTS': cls.SERVICE_REJECTS,
            'SERVICE_STAGE': cls.SERVICE_STAGE,
            'SERVICE_SUPPORTED_PLATFORMS': cls.SERVICE_SUPPORTED_PLATFORMS,
            'SERVICE_TIMEOUT': cls.SERVICE_TIMEOUT
        }

    @classmethod
    def get_service_version(cls):
        t = (
            version.SYSTEM_VERSION,
            version.FRAMEWORK_VERSION,
            cls.SERVICE_VERSION,
            cls.SERVICE_REVISION,
        )
        return '.'.join([str(v) for v in t])

    @staticmethod
    def parse_revision(revision):
        try:
            abs_path = os.path.abspath((inspect.stack()[1])[1])
            directory_of_1py = os.path.dirname(abs_path)
            return git_repo_revision(directory_of_1py)[:7]
        except Exception:
            print("Determining registration by fallback ")
            pass

        try:
            return revision.strip('$').split(':')[1].strip()[:7]
        except:
            return '0'

    def start_service(self):
        # Start this service. Common service start is performed and then
        # the derived services start() is invoked.
        # Services should perform any pre-fork (once per celery app) init
        # in the constructor. Any init/config that is not fork-safe or is
        # otherwise subprocess specific should be done here.

        try:
            self._ip = net.get_hostip()
        except:
            pass

        self.log.info('Service Starting: {}'.format(self.service_name()))

        # Tell the service to do its service specific imports.
        # We pop the CWD from the module search path to avoid
        # namespace collisions.
        cwd_save = sys.path.pop(0)
        self.import_service_deps()
        sys.path.insert(0, cwd_save)

        self.start()
        if self.SERVICE_SAFE_START:
            NamedQueue('safe-start-%s' % self.mac).push('up')

    def import_service_deps(self):
        """
        Do non-standard service specific imports.

        :return:
        """
        pass

    def _ensure_size_constraints(self, task):

        if not task or not task.result:
            return

        try:
            max_result_size = 1024 * 512
            serialized = json.dumps(task.as_service_result())
            if len(serialized) <= max_result_size:
                return

            task.oversized = True
            self.log.info("Result is oversized. Shrinking. ({})".format(len(serialized)))
            # Remove the tags and sections, leaving the score and tag_score intact.
            # Submit the oversized result as supplementary file.
            task.result['tags'] = []
            filename = '_'.join([self.service_name(), task.sha256, 'result.json'])
            result_path = os.path.join(self.working_directory, filename)
            with open(result_path, 'w') as f:
                f.write(serialized)

            file_info = identify.fileinfo(result_path)
            sha256 = file_info['sha256']
            mime = file_info['mime']

            task.supplementary.append(task.add_child(None, sha256, mime, 'oversized result', task.classification, result_path))

            oversize_notice_section = ResultSection(
                title_text="Result exceeded max size. Attached as supplementary file. Score has been preserved.")
            task.result['sections'] = [json.loads(json.dumps(oversize_notice_section))]
        except:
            self.log.exception("While shrinking oversized result")

    def handle_task(self, task):
        self.log.info('Start: {}/{} ({})'.format(task.sid, task.sha256, task.tag))
        self.task = task
        task.watermark(self.service_name(), self.get_service_version(), self.get_tool_version())
        task.save_result_flag = self.SERVICE_SAVE_RESULT

        # if task.profile:
        #     task.set_debug_info("serviced_on:%s" % self._ip)

        try:
            start_time = time.time()
            # First try to fetch from cache. If that misses,
            # run the service execute to get a fresh result.

            task.clear_extracted()
            task.clear_supplementary()
            # Pass it to the service for processing. Wrap it in ServiceRequest
            # facade so service writers don't see a request interface with 80 members.
            request = ServiceRequest(self, task)

            # Collect submission_tags
            if task.is_initial():
                self.submission_tags = {}
            else:
                self.submission_tags = task.get_submission_tags_name()

            old_result = self.execute(request)
            if old_result:
                self.log.warning("Service {} is using old convention "
                                 "returning result instead of setting "
                                 "it in request".format(self.service_name()))
                task.result = old_result
            elif task.save_result_flag and not task.result:
                self.log.info("Service {} supplied NO result at all. Creating empty result for the service...".format(self.service_name()))
                task.result = Result()

            task.milestones = {'service_started': start_time, 'service_completed': time.time()}
            if task.save_result_flag:
                task.result.finalize()
            self._success(task)
            # self._log_completion_record(task, (time.time() - start_time))
        except Exception as ex:
            print(ex)
            self._handle_execute_failure(task, ex, exceptions.get_stacktrace_info(ex))
            if not isinstance(ex, exceptions.RecoverableError):
                self.log.exception("While processing task: {}/{}".format(task.sid, task.sha256))
                raise
            else:
                self.log.info("While processing task: %s/%s", task.sid, task.sha256)
        finally:
            self._cleanup_working_directory()

    def _save_error(self, task, error_status, stack_info):
        task.error_message = stack_info
        task.error_status = error_status

        error = task.as_service_error()
        error_path = os.path.join(self.working_directory, 'error.json')
        with open(error_path, 'w') as f:
            json.dump(error, f)
        self.log.info("Saving error to: {}".format(error_path))

    def _save_result(self, task):
        if not task.save_result_flag:
            return None

        result = task.as_service_result()
        result_path = os.path.join(self.working_directory, 'result.json')
        with open(result_path, 'w') as f:
            json.dump(result, f)
        self.log.info("Saving result to: {}".format(result_path))

    def _cleanup_working_directory(self):
        # al_temp_dir = os.path.join(tempfile.gettempdir(), self.service_name().lower(), 'received')
        # try:
        #     if os.path.isdir(al_temp_dir):
        #         shutil.rmtree(al_temp_dir)
        # except:
        #     self.log.warning('Could not remove received directory: {}'.format(self._working_directory))
        self._working_directory = None

    def _log_completion_record(self, task, duration):
        self.log.info("Done:  {}/{} C:{} S:{} T:{:.3f} Z:{}".format(
                      task.sid, task.srl,
                      1 if task.from_cache else 0,
                      task.score or 0,
                      duration,
                      task.size))

    def _handle_execute_failure(self, task, exception, stack_info):
        # Get rid of result in case it was what caused the problem.
        task.result = None
        # Also get rid of extracted and supplementary
        task.clear_extracted()
        task.clear_supplementary()
        if isinstance(exception, exceptions.RecoverableError):
            self.log.info('Recoverable Service Error (%s/%s) %s: %s', task.sid, task.sha256, exception, stack_info)
            self._save_error(task, 'FAIL_RECOVERABLE', stack_info)
        else:
            self.log.error('Service Error (%s/%s) %s: %s', task.sid, task.sha256, exception, stack_info)
            self._save_error(task, 'FAIL_NONRECOVERABLE', stack_info)

    def stop_service(self):
        # Perform common stop routines and then invoke the child's stop().
        self.log.info('Service Stopping: {}'.format(self.service_name()))
        self.stop()

    @staticmethod
    def get_task_age(task):
        received = 0
        try:
            received = task.request.get('sent')
        except:
            pass
        if not received:
            return 0
        return time.time() - received

    def _success(self, task):
        # if task.result:
        #     tags = task.result.get('tags', None) or []
        #     if tags:
        #         ExpiringSet(task.get_tag_set_name()).add(*tags)

        self._ensure_size_constraints(task)

        task.success()
        self._save_result(task)

    def execute(self, request):
        # type: (ServiceRequest) -> None
        raise NotImplementedError('execute() not implemented.')

    @property
    def working_directory(self):
        al_temp_dir = os.path.join(tempfile.gettempdir(), self.service_name().lower(), 'completed')
        if not os.path.isdir(al_temp_dir):
            os.makedirs(al_temp_dir)
        if self._working_directory is None:
            self._working_directory = al_temp_dir
        return self._working_directory


class BatchServiceBase(ServiceBase):
    BATCH_SERVICE = True
    BATCH_SIZE = 50
    BATCH_TIMEOUT_SECS = 3

    SUPPORTS_SRBATCH = False

    def _download_batch(self, tasks, dest_dir=None):
        succeeded = {}
        failed = []
        if dest_dir is None:
            dest_dir = self.working_directory

        for task in tasks:
            try:
                local_path = os.path.join(dest_dir, os.path.basename(task.srl))
                self.transport.download(task.srl, local_path)
                succeeded[local_path] = task
            except Exception as ex:
                failed.append((task, ex))
                msg = exceptions.get_stacktrace_info(ex)
                task.nonrecoverable_failure(msg)
                self._save_error(task)
        return succeeded, failed

    def _fail_all_in_batch(self, task_batch, msg, recoverable=True):
        for task in task_batch:
            if recoverable:
                task.recoverable_failure(msg)
            else:
                task.nonrecoverable_failure(msg)
            self._save_error(task)

    def _finalize(self, task, duration, batch_size):
        if task.profile:
            task.set_debug_info("serviced_on:%s" % self._ip)
        if task.save_result_flag:
            task.result.finalize()
        self._log_completion_record(task, (duration / batch_size))
        self._success(task)

    def execute(self, _task):
        raise Exception('execute() called on a batch service. Expected execute_batch().')

    def execute_batch(self, _batch):
        raise NotImplementedError('execute_batch() not implemented in BatchService.')

    def _handle_task_batch(self, tasks):
        """ Handle a batch of tasks at once.
        Argument: A list of Task objects
        """
        # Expedite any tasks with cached results.
        start_time = time.time()
        num_tasks = len(tasks)
        self.log.info('StartBatch: %s', num_tasks)

        for task in tasks:
            task.watermark(self.service_name(), self.get_service_version())
            task.save_result_flag = self.SERVICE_SAVE_RESULT

        plan = [(self._process_cached_task, (task,), tid) for tid, task in enumerate(tasks)]
        result = execute_concurrently(plan)
        if '_exception_' in result:
            failed = result.pop('_exception_')
            self.log.error("Exception in concurrent execution: %s", str(failed))

        cache_misses = [cache_miss for cache_miss in result.itervalues() if cache_miss]

        self.log.info("Cache status: H:%s M:%s" % (len(tasks) - len(cache_misses), len(cache_misses)))

        successful = []
        try:
            # execute_batch will assign the results to each task in place.
            # and is also responsible for setting success or failure state.
            if not cache_misses:
                self.log.info("No tasks left after cache interrogation")
            elif self.SUPPORTS_SRBATCH:
                batch = ServiceRequestBatch(self, cache_misses)
                self.execute_batch(batch)
                for request in batch.requests:
                    if request.successful:
                        request.error_text = ''
                        successful.append(request.task)
                    else:
                        if request.error_is_recoverable:
                            self._handle_execute_failure(request.task,
                                                         exceptions.RecoverableError(request.error_text),
                                                         request.error_text)
                        else:
                            self._handle_execute_failure(request.task,
                                                         exceptions.NonRecoverableError(request.error_text),
                                                         request.error_text)

            else:
                self.execute_batch(cache_misses)
                successful.extend(cache_misses)
        except Exception as ex:
            self.log.exception('While processing batch of size %s. Failing all.', len(cache_misses))
            msg = exceptions.get_stacktrace_info(ex)
            self._fail_all_in_batch(cache_misses, msg, recoverable=False)
            self._cleanup_working_directory()
            return

        duration = time.time() - start_time
        self.log.info('DoneBatch: %s. T:%s', len(tasks), duration)

        if len(successful) > 0:
            plan = [(self._finalize, (task, duration, len(tasks)), tid) for tid, task in enumerate(successful)]
            execute_concurrently(plan)

        self._cleanup_working_directory()


class ServiceRequest(object):
    def __init__(self, service, task):
        # type: (ServiceBase, Task) -> None

        self.log = logging.getLogger('assemblyline.svc.{}'.format(service.service_name().lower()))

        self.srl = task.sha256
        self.sid = task.sid
        # self.config = task.config
        self.tag = task.tag
        self.md5 = task.md5
        self.sha1 = task.sha1
        self.sha256 = task.sha256
        # self.priority = task.priority
        # self.ignore_filtering = task.ignore_filtering
        self.task = task
        # self.local_path = ''
        # self.successful = True
        # self.error_is_recoverable = True
        # self.error_text = None
        # self.current_score = task.max_score
        self.deep_scan = task.deep_scan
        self.extracted = task.extracted
        self.max_extracted = task.max_extracted
        self.path = task.sha256  # TODO: self.path = task.path or task.sha256

        self._svc = service

    @property
    def result(self):
        # type: () -> Result
        return self.task.result

    @result.setter
    def result(self, value):
        self.task.result = value

    def add_extracted(self, name, text, display_name=None, classification=None, submission_tag=None, normalize=lambda x: x):
        """
        Add an extracted file for additional processing.

        :param name: Path to file to attach
        :param text: Descriptive text about the file
        :param display_name: Optional display text
        :param classification: The classification of this extracted file. Defaults to current classification.
        :param submission_tag:
        :return: None
        """
        # Move extracted file to working directory for compatibility with ALv4
        file_name = display_name or normalize(name)
        original_file_path = name
        new_file_path = os.path.join(self._svc.working_directory, file_name)

        return self.task.add_extracted(
            original_file_path, new_file_path, text, file_name, classification or self._svc.SERVICE_CLASSIFICATION
        )

    def add_supplementary(self, name, text, display_name=None, classification=None, normalize=lambda x: x):
        # Move supplementary file to working directory for compatibility with ALv4
        file_name = display_name or normalize(name)
        original_file_path = name
        new_file_path = os.path.join(self._svc.working_directory, file_name)

        return self.task.add_supplementary(
            original_file_path, new_file_path, text, file_name, classification or self._svc.SERVICE_CLASSIFICATION
        )

    def download(self):
        file_path = os.path.join(tempfile.gettempdir(), self.task.service_name.lower(), 'received', self.sha256)
        if not os.path.exists(file_path):
            raise Exception('Download failed. Not found on local filesystem')

        received_sha256 = digests.get_sha256_for_file(file_path)
        if received_sha256 != self.sha256:
           raise Exception('SHA256 mismatch between requested and downloaded file. {} != {}'.format(self.sha256, received_sha256))
        return file_path

    def set_service_context(self, msg):
        self.task.report_service_context(msg)

    def tempfile(self, sha256):
        return os.path.join(self._svc.working_directory, sha256)

    def get_param(self, name):
        # Does the parameter exist in the class?
        params_code = [x for x in self._svc.SERVICE_DEFAULT_SUBMISSION_PARAMS if x["name"] == name]
        params = [x for x in self.task.service_config if x == name]
        if params:
            return params[0]
        else:
            return params_code[0]['value']

    def drop(self):
        self.task.drop()


class ServiceRequestBatch(object):
    def __init__(self, service, tasks):
        self._service = service
        self.requests = [ServiceRequest(service, t) for t in tasks]
        # self.request_by_srl = {}
        self.batchid = uuid.uuid4().get_hex()
        # self._index_requests()
        self.request_by_localpath = {}
        self.batch_working_dir = os.path.join(tempfile.gettempdir(), self._service.service_name, self.batchid)

    def download(self):
        download_directory = self.batch_working_dir
        os.makedirs(download_directory)

        for request in self.requests:
            local_path = ""
            try:
                local_path = os.path.join(download_directory,
                                          os.path.basename(request.sha256))
                self._service.transport.download(request.sha256, local_path)
                received_sha256 = digests.get_sha256_for_file(local_path)
                if received_sha256 != request.sha256:
                    raise Exception('SHA256 mismatch between requested and downloaded file. {} != {}'.format(request.sha256, received_sha256))
                request.successful = True
                request.local_path = local_path
            except Exception as ex:
                self._service.log.error("Failed to download: %s - %s", local_path, str(ex))
                msg = exceptions.get_stacktrace_info(ex)
                request.successful = False
                request.error_text = msg
                if not "SHA256 mismatch" in ex:
                    request.error_is_recoverable = True

        # often batch services will know the filename that they processed
        # and want to get the original request associated with it.
        # self._index_by_localpath()

        return download_directory
