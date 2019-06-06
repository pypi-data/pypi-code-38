import datetime
import logging
import os
import sys
import threading
from multiprocessing import Process
from time import sleep
from typing import NamedTuple

# We may need below, we may not. What can I say? Dill waters run deep.
import dill

from pyqalx.config import BotConfig
from pyqalx.core.adapters import QalxQueue, QalxAdapter, QalxSession, QalxWorker
from pyqalx.core.errors import QalxBotInitialisationFailed
from pyqalx.core.errors import QalxError, QalxConfigError
from pyqalx.core.log import exception_hook, QalxRotatingFileHandler, \
    QalxLogFormatter
from pyqalx.core.signals import QalxSignal

logger = logging.getLogger(__name__)

dill.settings['recurse'] = True


def do_nowt(*args, **kwargs):
    pass


def do_nowt_right(*args, **kwargs):
    return True


class QalxJob:
    """a Job to process

    :param worker_process:
    :type worker_process Worker:
    """
    __slots__ = ('worker_adapter', 'entity_adapter', 'entity', 'session',
                 'state', 'options', 'progress', 'warnings', 'errors',
                 'worker_logger', '_current_step', '_process',
                 '_worker_entity', '_bot_entity', '_queue_message',
                 '_step_results')

    def __init__(self, worker_process):
        self._process = worker_process
        self.worker_adapter = worker_process.worker_adapter
        self._bot_entity = worker_process.bot_entity
        self._worker_entity = worker_process.api_entity
        self.session = worker_process.session
        self.worker_logger = worker_process.logger

        self._current_step = "class init"
        self._step_results = []

    @property
    def log(self):
        return self.worker_logger

    @property
    def e(self):
        """shortcut to QalxJob().entity"""
        return self.entity

    @property
    def s(self):
        """shortcut to QalxJob().session"""
        return self.session

    def stop_processing(self):
        """
        Stop the worker from processing.  Will cause the worker to wait until
        it receives a `resume` signal
        """
        self.worker_adapter.stop(entity=self._worker_entity,
                                 bot_entity=self._bot_entity)

    def resume_processing(self):
        """
        Resume the worker.
        """
        self.worker_adapter.resume(entity=self._worker_entity,
                                   bot_entity=self._bot_entity)

    def terminate(self, warm=True, requeue_job=False):
        """
        The job has been told to terminate the worker

        :param warm: If True will completely finish running through the
                     processes for the current job.  If False will exit as soon
                     as the current process function is complete
        :param requeue_job: Should the job be requeued if we are terminating
                            with `warm=False`
        """
        self.worker_adapter.terminate(entity=self._worker_entity,
                                      bot_entity=self._bot_entity,
                                      warm=warm,
                                      requeue_job=requeue_job)

    def publish_status(self, status_string="", status_dict=None):
        """update the status of the worker

        :param status_string: short message about the worker status
        :type status_string: str
        :param status_dict: structured status data
        """
        status = {
            'time': datetime.datetime.now().isoformat(),
            'message': status_string
        }
        if status_dict is not None:
            status.update(status_dict)
        self.worker_adapter.update_status(entity=self._worker_entity,
                                          bot_entity=self._bot_entity,
                                          status=status)

    def add_step_result(self, success=True, result_data=None):
        """indicate success and add info about the current step

        :param success: was the step successful or not
        :type success: bool
        :param result_data: data from the result
        :type result_data: dict
        """
        self._step_results.append(StepResult(success=success,
                                             step_name=self._current_step,
                                             result_data=result_data))

    @property
    def last_step_result(self):
        if self._step_results:
            return self._step_results[-1]
        else:
            return None

    def get_entity(self, entity_type, entity_guid):
        """
        get an entity

        :param entity_type: the type of entity e.g. item, set, group
        :type entity_type: str
        :param entity_guid: the guid of the entity
        :type entity_guid: str
        :return: a child of pyqalx.core.entities.QalxEntity
        """
        adapter = getattr(self.session, entity_type)
        self.entity_adapter = adapter
        self.entity = adapter.get(entity_guid,
                                  config=self.session.config)
        return self.entity

    def add_item_data(self, item_key, data, meta=None):
        """
        helper method to add data item to the set

        :param item_key: key on the set to add the item as
        :type item_key: str
        :param data: data to add
        :param meta: metadata
        :return:
        """
        if not (self.entity.entity_type == "set"):
            raise TypeError("Method add_item_data only works on jobs with a set entity.")
        self.entity['items'][item_key] = self.session.item.add(data=data, meta=meta)
        self.save_entity()
        return self.entity['items'][item_key]

    def save_entity(self):
        """

        :return: a child of pyqalx.core.entities.QalxEntity
        """
        # Always ensure that the entity on the adapter is fully up to date
        # with the entity on the job.
        # self.entity_adapter.entity = self.entity
        self.entity_adapter.save(entity=self.entity)
        return self.entity

    def reload_entity(self):
        """

        :return: a child of pyqalx.core.entities.QalxEntity
        """
        # Always ensure that the entity on the adapter is fully up to date
        # with the entity on the job.
        # self.entity_adapter.entity = self.entity
        self.entity = self.entity_adapter.reload(entity=self.entity)
        return self.entity


class StepResult(NamedTuple):
    step_name: str = ""
    success: bool = False
    result_data: dict = {}


class Bot:
    __slots__ = (
        "name", "queue_name", "initialisation_function", "begin_function", "preload_function", "onload_function",
        "preprocess_function", "process_function", "precompletion_function", "postprocess_function", "onwait_function",
        "ontermination_function", "bot_entity", "bot_adapter"
    )

    def __init__(self,
                 bot_name,
                 queue_name):
        self.name = bot_name

        self.queue_name = queue_name
        # bot lifecycle functions
        self.initialisation_function = do_nowt_right
        self.begin_function = do_nowt
        self.preload_function = do_nowt
        self.onload_function = do_nowt
        self.preprocess_function = do_nowt
        self.process_function = do_nowt
        self.precompletion_function = do_nowt
        self.postprocess_function = do_nowt
        self.onwait_function = do_nowt
        self.ontermination_function = do_nowt

    def _collect_steps(self):
        steps = {}
        for fn in self.__dir__():
            if fn.endswith("_function"):

                fn_attr = getattr(self, fn)
                if not fn_attr in [do_nowt, do_nowt_right]:
                    steps[fn] = dill.dumps(fn_attr)  # serialise functions
        return steps

    def start(self,
              qalx_session_class=None,
              user_profile_name="default",
              user_config_class=None,
              bot_profile_name="default",
              bot_config_class=None,
              skip_ini=False,
              processes=1):

        if qalx_session_class is None:
            qalx_session_class = QalxSession

        user_session = qalx_session_class(profile_name=user_profile_name,
                                          config_class=user_config_class,
                                          skip_ini=skip_ini)

        if bot_config_class is None:
            bot_config_class = BotConfig

        # This configures logging to use the config settings specified
        # on the bot
        bot_session = qalx_session_class(
            profile_name=bot_profile_name,
            config_class=bot_config_class,
            skip_ini=skip_ini)

        self.bot_entity = user_session.bot.add(name=self.name,
                                               config=bot_session.config)

        self.bot_adapter = bot_session.bot

        if self.initialisation_function:
            init_result = self.initialisation_function(self.bot_adapter.session)
            logger.debug(f"Initialisation function returns {init_result}")
            if not init_result:
                raise QalxBotInitialisationFailed("The initialisation function returned a False-like value.")
        steps = self._collect_steps()

        # We need to update the config with the Bot Token
        self.bot_adapter.session._update_config(config={'TOKEN': self.bot_entity['info']['credentials']['token']})

        self.bot_entity = \
            self.bot_adapter.replace_workers(bot_entity=self.bot_entity,
                                             workers=processes)

        workers = []
        # We use the same session and adapter for all workers

        worker_adapter = QalxWorker(session=self.bot_adapter.session)

        for worker in range(processes):
            workers.append(Worker(steps,
                                  self.queue_name,
                                  self.bot_entity,
                                  self.bot_entity['workers'][worker],
                                  worker_adapter,
                                  index=worker))
            logger.debug(f"Created worker {worker} to read from {self.queue_name}")
        [
            p.start() for p in workers
        ]
        [
            p.join() for p in workers
        ]
        logger.debug("Workers joined.")

    def initialisation(self, func):
        """decorator to to register the initialisation

        `initialisation` is executed with no argument
        :param func: function to be executed
        :return:
        """
        self.initialisation_function = func

    def begin(self, func):
        """decorator to to register the begin

        `begin` is executed with no argument
        :param func: function to be executed
        :return:
        """
        self.begin_function = func

    def preload(self, func):
        """decorator executed before entity is loaded from qalx.

        `preload` is executed with a single qalx.QueueMessage argument.
        :param func: function to be executed
        :return:
        """
        self.preload_function = func

    def onload(self, func):
        """decorator to register the onload

        :param func: function to be executed
        :return:
        """
        self.onload_function = func

    def preprocess(self, func):
        """decorator to register preprocess function

        :param func: function to register
        :return:
        """
        self.preprocess_function = func

    def process(self, func):
        """decorator to register process function

        :param func: function to register
        :return:
        """
        self.process_function = func

    def precompletion(self, func):
        """decorator to register precompletion function

        :param func: function to register
        :return:
        """
        self.precompletion_function = func

    def postprocess(self, func):
        """decorator to register postprocess function

        :param func: function to register
        :return:
        """
        self.postprocess_function = func

    def onwait(self, func):
        """decorator to register onwait function

        :param func: function to register
        :return:
        """
        self.onwait_function = func

    def ontermination(self, func):
        """decorator to register ontermination function

        :param func: function to register
        :return:
        """
        self.ontermination_function = func


class Worker(Process):
    """

    exit codes (start at 72590):

        - 72590 base exit code
        - 72591 warm exit
        - 72592 cold exit
        - 72593 config triggered (e.g. KILL_AFTER)
    """

    def __init__(self, steps, queue_name, bot_entity, api_entity,
                 worker_adapter, index, **kwargs):
        super(Worker, self).__init__(**kwargs)
        self._steps = steps
        self.queue_name = queue_name
        self.bot_entity = bot_entity
        self.api_entity = api_entity
        self.worker_adapter = worker_adapter
        self.session = self.worker_adapter.session
        self.stop = False
        self.config = self.session.config
        self.index = index
        self.bot_signal = None
        self.worker_signal = None

    def configure_logging(self, index):
        """
        Configures the logger for the Worker. Each Worker logs to its own
        file. This prevents issues with multiple processes trying to write
        to the same file
        :param index: The index of the worker to use in the filename
        :return: An instance of `logging.Logger`
        """
        directory = self.config["WORKER_LOG_FILE_DIR"]
        level = self.config['LOGGING_LEVEL']
        if os.path.isdir(directory) is False:
            raise QalxConfigError(f"WORKER_LOG_FILE_DIR config value "
                                  f"not a valid directory. Got `{directory}`")

        worker_logger = logging.getLogger(f'pyqalx.worker.{index}')

        filename = os.path.join(directory,
                                f'.worker_{self.bot_entity["name"]}.{index}.log')
        handler = QalxRotatingFileHandler(filename=filename)

        handler.setFormatter(QalxLogFormatter())
        handler.setLevel(level)
        worker_logger.addHandler(handler)
        worker_logger.setLevel(level)
        return worker_logger

    def _check_bot_signal(self):
        """
        Checks the bot signal and either terminates the bot or stops it
        """
        self.bot_signal = self.session.bot.get_signal(self.bot_entity)

        if self.bot_signal.terminate_warm:
            self._do_exit(**QalxSignal._bot_triggered_exit_update())
        else:
            self.stop = self.bot_signal.stop

    def _reload_signal(self):
        """
        Helper method for reloading the signal for this worker
        """
        self.worker_signal = self.worker_adapter.get_signal(self.api_entity,
                                                            bot_entity=self.bot_entity)

    def _check_worker_signal(self):
        """
        Reload the worker signal and either terminates the worker or stops it
        """
        self._reload_signal()

        if self.worker_signal.terminate_warm:
            self._do_exit(**QalxSignal._bot_triggered_exit_update())
        else:
            self.stop = self.worker_signal.stop

    def _do_exit(self, update, code=QalxSignal.BASE_EXIT_CODE):
        self.job._current_step = 'OnTerminate'
        onterm = self.steps.get('ontermination_function')
        if onterm:
            onterm(self.job)
        self.job.publish_status(update)
        sys.exit(code)

    def _check_cold_exit(self, reload_signal=True):
        """
        Reloads the worker signal and checks whether we should do a cold
        termination
        """
        if reload_signal:
            self._reload_signal()

        if self.worker_signal.terminate_cold:
            # The worker has been asked to cold exit for some reason.
            # Check if the job needs to go back on the queue or if we can delete it
            if self.job._queue_message:
                if self.worker_signal.requeue_job:
                    self.job._queue_message._stop_heartbeat()
                else:
                    self._delete_message()
            self._do_exit(**QalxSignal._cold_exit_update())

    def _check_warm_exit(self):
        """
        Reloads the worker signal and checks whether we should do a warm
        termination
        """
        self._reload_signal()

        if self.worker_signal.terminate_warm:
            # The worker has been asked to warm exit for some reason.
            # The job will have finished and the message should have been deleted.
            self._do_exit(**QalxSignal._warm_exit_update())

    def _delete_message(self):
        """
        Helper function for stopping any heartbeat on the job and
        deleting the message
        """
        if getattr(self.job, "_queue_message", None):
            self.job._queue_message._stop_heartbeat()
            self.queue.delete_message(self.job._queue_message)

    def _wait_with_spreading(self, spread_factor):
        """
        we want to wait for a while before trying something again and wait longer and
        longer every time up to a maximum. This is to help limit the request count to
        qalx while staying responsive.

        :return: the next spreading factor to use
        """

        time_to_wait = int(self.config['Q_WAITTIMESECONDS'])
        max_spreading = int(self.config['Q_WAITTIMEMAXSPREADING'])
        self.job._queue_message = None
        self.job._current_step = 'OnWait'
        if self.steps.get('onwait_function') is not None:
            self.steps['onwait_function'](self.job)
        total_wait_seconds = time_to_wait * spread_factor
        sleep(total_wait_seconds)
        self.logger.debug(f"wait for {total_wait_seconds}s")
        self._check_bot_signal()
        self._check_worker_signal()
        self._check_cold_exit(reload_signal=False)  # we reloaded in prev line
        next_spread = spread_factor + 1
        # never spread beyond a max factor
        return min(max_spreading, next_spread)

    def _continue_processing(self):
        if self.job.last_step_result:
            return (not self.stop) and self.job.last_step_result.success
        else:
            return not self.stop

    def _run_functions(self):
        # Each worker has its own dedicated logger
        self.logger = self.configure_logging(index=self.index)
        self.job = QalxJob(self)
        _startup = True
        # avoid pickle errors
        self.steps = {}
        for f_name, f_dill in self._steps.items():  # de-serialise functions
            self.logger.debug(f"try to undill step {f_name}")
            try:
                self.steps[f_name] = dill.loads(f_dill)
            except TypeError:
                self.steps[f_name] = f_dill

        self.logger.debug(f"running")
        if self.steps.get('begin_function'):
            self.job._current_step = "Begin"

            self.steps.get('begin_function')(self.session)
            self._check_bot_signal()
            self._check_worker_signal()
            self._check_cold_exit(reload_signal=False)

        # get queue
        queue_adapter = QalxQueue(session=self.session)
        self.queue = queue_adapter.get_by_name(self.queue_name)

        kill_after = self.config['KILL_AFTER']
        spread_factor = 1
        no_message_attempts = 0

        while True:
            if self.stop:
                spread_factor = self._wait_with_spreading(spread_factor)
                self.logger.debug(f"Stop signal on Worker waited with factor {spread_factor}")
            else:
                q_msgs = queue_adapter.get_messages(queue=self.queue)
                self.logger.debug(f"got {len(q_msgs)} messages")
                if q_msgs:
                    for q_msg in q_msgs:
                        if not _startup:
                            self.job = QalxJob(self)
                        _startup = False
                        self.job._queue_message = q_msg
                        self.logger.debug(f"process {q_msg.body}")
                        self._process_functions()
                        self._check_bot_signal()
                        self._check_worker_signal()
                    no_message_attempts = 0  # reset the attempt counter
                    spread_factor = 1  # reset any wait spreading
                else:
                    spread_factor = self._wait_with_spreading(spread_factor)
                    no_message_attempts += 1

            if (kill_after is not None) and (no_message_attempts >= int(kill_after)):
                self._do_exit("KILL_AFTER reached", 72593)

    def _process_functions(self):
        def process_as_far_as_possible(functions):
            for fn, step_name in functions:
                if self._continue_processing():
                    self.job._current_step = step_name
                    try:
                        fn(self.job)
                    except Exception:
                        # This needs to be a bare exception to handle
                        # something going wrong with the user defined functions
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        # Send as a `QalxError` to our handler otherwise we
                        # risk consuming exceptions from the users application
                        exception_hook(exc_type=QalxError,
                                       exc_value=exc_value,
                                       exc_traceback=exc_traceback,
                                       extra={'entity_guid': self.job.entity['guid'],
                                              'entity_type': self.job.entity.entity_type},
                                       logger=self.logger)

                    # check if we need to cold exit after every function
                    self._check_cold_exit()
                    if self.config.getboolean('SAVE_INTERMITTENT'):
                        self.job.save_entity()
                else:
                    break
            if not self.config.getboolean('SKIP_FINAL_SAVE'):
                self.job.save_entity()

            # We delete the message from the queue once we've processed it
            self._delete_message()
            return self.job

        # PreLoad
        if self.steps.get('preload_function'):
            self.job._current_step = 'PreLoad'
            self.steps.get('preload_function')(self.job)
            self._check_cold_exit()
        if self._continue_processing():
            # Process steps
            steps = ('OnLoad', 'PreProcess', 'Process', 'PreCompletion', 'PostProcess')
            process_functions = [
                (self.steps.get(f'{s.lower()}_function'), s) for s in steps if self.steps.get(f'{s.lower()}_function')
            ]

            entity_type = self.job._queue_message.body['entity_type']
            entity_guid = self.job._queue_message.body['entity_guid']
            self.job.get_entity(entity_type, entity_guid)

            t = threading.Thread(target=process_as_far_as_possible,
                                 args=(process_functions,))
            t.start()
            while t.is_alive():
                # Start a heartbeat while we process this message.
                visibility = self.config["MSG_BLACKOUTSECONDS"]
                self.job._queue_message._do_heartbeat(visibility=visibility,
                                                      queue=self.queue)
        else:
            self._delete_message()

    def run(self):
        """
        Run our custom functions.  Catch any exception
        that may occur with it and pass that to our custom
        uncaught exception handler
        """
        try:
            self._run_functions()
        except Exception:
            # This needs to be a bare exception to handle something going
            # wrong with the Worker
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # Send as a `QalxError` to our handler otherwise we
            # risk consuming exceptions from the users application
            exception_hook(exc_type=QalxError,
                           exc_value=exc_value,
                           exc_traceback=exc_traceback,
                           logger=self.logger)
