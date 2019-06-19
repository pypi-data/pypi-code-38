#!/usr/bin/env python

import json
import logging
import os
import signal
import sys
import tempfile
import threading
import time

import yaml
from Queue import Empty
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import EventQueue

from alv3_service.common import log as al_log
from alv3_service.common.dict_utils import recursive_update
from alv3_service.common.importing import load_module_by_path
from alv3_service.common.mock_modules import modules1, modules2
from alv3_service.common.task import Task

SERVICE_PATH =os.environ['SERVICE_PATH']
SERVICE_NAME = SERVICE_PATH.split(".")[-1].lower()
SHUTDOWN_SECONDS_LIMIT = 10

al_log.init_logging()
LOGGER = logging.getLogger('assemblyline.svc.{}'.format(SERVICE_NAME))

modules1()
modules2()


class FileEventHandler(PatternMatchingEventHandler):
    def __init__(self, queue, patterns):
        PatternMatchingEventHandler.__init__(self, patterns=patterns)
        self.queue = queue

    def process(self, event):
        '''
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        '''

        if event.src_path.endswith('task.json'):
            self.queue.put(event.src_path)

    def on_created(self, event):
        self.process(event)


class FileWatcher(object):
    def __init__(self, queue, watch_path):
        self.watch_path = watch_path
        self.event_handler = None
        self.observer = None
        self.queue = queue

    def start(self):
        patt = ['*.json']
        event_handler = FileEventHandler(self.queue, patterns=patt)
        self.observer = Observer()
        self.observer.schedule(event_handler, path=self.watch_path)
        self.observer.daemon = True
        LOGGER.info("Started watching folder for tasks: {}".format(self.watch_path))
        self.observer.start()

    def stop(self):
        self.observer.stop()
        LOGGER.info("Stopped watching folder for tasks: {}".format(self.watch_path))
        pass


class RunService(threading.Thread):
    """
    Inheriting from thread so that the main work is done off the main thread.
    This lets the main thread handle interrupts properly, even when the workload
    makes a blocking call that would normally stop this.
    """

    def __init__(self, shutdown_timeout=SHUTDOWN_SECONDS_LIMIT):
        super(RunService, self).__init__()

        self.running = None
        self._exception = None
        self._traceback = None
        self._shutdown_timeout = shutdown_timeout

        self.classification_yml_file = '/etc/assemblyline/classification.yml'
        self.config_yml_file = '/etc/assemblyline/service_config.yml'
        self.constants_json_file = '/etc/assemblyline/constants.json'

        self.shutdown_timeout = shutdown_timeout
        self.status = None

        self.wait_start = None
        self.queue = EventQueue()
        self.file_watcher = None

        self.service_name = None
        self.service_version = None
        self.service_tool_version = None
        self.service_category = None
        self.service_stage = None
        self.file_required = None
        self.received_folder_path = None

    def __enter__(self):
        LOGGER.info("Initialized")
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.close()
        if _exc_type is not None:
            LOGGER.exception("Terminated because of an {} exception".format(_exc_type))
        else:
            LOGGER.info('Terminated')

    def __stop(self):
        """Hard stop"""
        time.sleep(self._shutdown_timeout)
        LOGGER.error(str(threading.enumerate()))
        LOGGER.error("Server has shutdown hard after waiting {} seconds to stop".format(self._shutdown_timeout))
        exit(1)

    def close(self):
        pass

    def interrupt_handler(self, _signum, _stack_frame):
        LOGGER.info("Instance caught signal. Coming down...")
        self.stop()

    def raising_join(self):
        self.join()
        if self._traceback and self._exception:
            raise self._exception.with_traceback(self._traceback)

    def run(self):
        try:
            self.try_run()
        except Exception:
            _, self._exception, self._traceback = sys.exc_info()
            LOGGER.exception("Exiting:")

    def serve_forever(self):
        self.start()
        self.join()

    def start(self):
        """Start the server workload."""
        self.running = True
        super(RunService, self).start()
        LOGGER.info("Started")
        signal.signal(signal.SIGINT, self.interrupt_handler)
        signal.signal(signal.SIGTERM, self.interrupt_handler)

    def stop(self):
        """Ask nicely for the server to stop.

        After a timeout, a hard stop will be triggered.
        """
        # The running loops should stop within a few seconds of this flag being set.
        self.running = False

        # If it doesn't stop within a few seconds, this other thread should kill the entire process
        stop_thread = threading.Thread(target=self.__stop)
        stop_thread.daemon = True
        stop_thread.start()

    def try_run(self):
        try:
            self.svc_class = load_module_by_path(SERVICE_PATH)
        except:
            LOGGER.error("Could not find service in path.")
            raise

        cfg = self.get_service_config()

        self.received_folder_path = os.path.join(tempfile.gettempdir(), SERVICE_NAME.lower(), 'received')
        if not os.path.isdir(self.received_folder_path):
            os.makedirs(self.received_folder_path)

        # Start the file watcher
        self.file_watcher = FileWatcher(self.queue, self.received_folder_path)
        self.file_watcher.start()

        service = self.svc_class(cfg)
        service.start_service()

        try:
            while self.running:
                try:
                    task_json_path = self.queue.get(timeout=1)
                except Empty:
                    continue

                LOGGER.info("Task found in: {}".format(task_json_path))
                try:
                    with open(task_json_path, 'r') as f:
                        task = Task(json.load(f))
                    service.handle_task(task)

                    while os.path.exists(task_json_path):
                        time.sleep(1)

                    self.queue.task_done()
                except IOError:
                    pass

        except Exception as e:
            LOGGER.error(str(e))
        finally:
            self.file_watcher.stop()
            service.stop_service()


    def get_service_config(self, yml_config=None):
        if yml_config is None:
            yml_config = '/etc/assemblyline/service_config.yml'

        service_config = {}
        default_file = os.path.join(os.path.dirname(__file__), 'common', 'service_config.yml')
        if os.path.exists(default_file):
            with open(default_file, 'r') as default_fh:
                default_service_config = yaml.safe_load(default_fh.read())
                if default_service_config:
                    service_config.update(default_service_config)

        # Load modifiers from the service
        service = self.svc_class(cfg={})
        service_data = service.get_default_config()
        service_config = recursive_update(service_config, service_data)
        service_config['SERVICE_VERSION'] = service.get_service_version()
        service_config['SERVICE_TOOL_VERSION'] = service.get_tool_version()

        with open(yml_config, 'w') as yml_fh:
            yaml.safe_dump(service_config, yml_fh)

        return service_config['SERVICE_DEFAULT_CONFIG']


if __name__ == '__main__':
    RunService().serve_forever()
