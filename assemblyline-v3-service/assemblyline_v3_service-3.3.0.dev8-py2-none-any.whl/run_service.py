#!/usr/bin/env python

# Run a standalone AL service

import json
import logging
import os
import tempfile
import time

import Queue
import pyinotify
import yaml

from alv3_service.common import log as al_log
from alv3_service.common.mock_modules import modules1, modules2
from alv3_service.common.task import Task
from assemblyline.common.dict_utils import recursive_update
from assemblyline.common.importing import load_module_by_path

modules1()
modules2()

current_task = None
previous_task = None


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        global current_task, previous_task

        if event.pathname.endswith('_task.json'):
            if previous_task != os.path.basename(event.pathname):
                previous_task = current_task
                current_task = os.path.basename(event.pathname)
                task_queue.put(current_task)


def run_service():
    service = svc_class(cfg)
    service.start_service()

    folder_path = os.path.join(tempfile.gettempdir(), svc_name, 'received')
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)

    wm = pyinotify.WatchManager()  # Watch Manager
    notifier = pyinotify.ThreadedNotifier(wm, EventHandler(), read_freq=2)
    notifier.coalesce_events()
    notifier.start()

    wm.add_watch(folder_path, pyinotify.IN_CREATE, rec=True)

    try:
        while True:
            item = task_queue.get()
            if item is None:
                time.sleep(1)
                continue

            task_path = os.path.join(folder_path, item)
            log.info("Task found in: {}".format(task_path))
            try:
                with open(task_path, 'r') as f:
                    task = Task(json.load(f))
                service.handle_task(task)

                while os.path.exists(task_path):
                    time.sleep(1)
                task_queue.task_done()
            except IOError:
                pass
    except Exception as e:
        log.error(str(e))
    finally:
        notifier.stop()
        service.stop_service()


def get_service_config(yml_config=None):
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
    service = svc_class()
    service_data = service.get_default_config()
    service_config = recursive_update(service_config, service_data)
    service_config['SERVICE_TOOL_VERSION'] = service.get_tool_version()

    with open(yml_config, 'w') as yml_fh:
        yaml.safe_dump(service_config, yml_fh)

    return service_config['SERVICE_DEFAULT_CONFIG']


if __name__ == '__main__':

    name = os.environ['SERVICE_PATH']

    svc_name = name.split(".")[-1].lower()
    al_log.init_logging(log_level=logging.INFO)
    log = logging.getLogger('assemblyline.svc.{}'.format(svc_name))

    task_queue = Queue.Queue(maxsize=0)

    try:
        svc_class = load_module_by_path(name)
    except:
        log.error("Could not find service in path.")
        raise

    cfg = get_service_config()

    try:
        run_service()
    except Exception as e:
        log.error(str(e))
