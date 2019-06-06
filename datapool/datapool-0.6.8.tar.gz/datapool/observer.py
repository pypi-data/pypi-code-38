# encoding: utf-8
from __future__ import absolute_import, division, print_function

import glob
import os.path
import sys
import time
from hashlib import sha1
from threading import Lock, Thread

from watchdog.events import (FileCreatedEvent, FileModifiedEvent,
                             FileSystemEventHandler)

IS_MAC = sys.platform == "darwin"

CREATED_EVENT = "created"
MODIFIED_EVENT = "modified"
ILLEGAL_EVENT = "illegal"


class _EventHandler(FileSystemEventHandler):
    """handles file creation and modificaiont events for .raw and .yaml files
    """

    def __init__(self, root_folder, call_back, logger):
        super().__init__()
        self._call_back = call_back
        self.root_folder = root_folder
        self.logger = logger
        self.last_hash = {}
        self.hash_lock = Lock()

    def compute_hash(self, event):
        """some marker files are gone very fast and are not interesting anyway
        so we could get here issues reading the file. In this case we compute None
        and the caller of this method will handle this.
        """
        try:
            content = open(os.path.join(self.root_folder, event.src_path), "rb").read()
        except IOError:
            return None
        hasher = sha1()
        hasher.update(content)
        digest = hasher.hexdigest()
        return digest

    def update_hash(self, event, hash_):
        self.last_hash[event.src_path] = hash_

    def hash_changed(self, event, hash_):
        return self.last_hash.get(event.src_path) != hash_

    def remove_hash(self, event):
        self.last_hash.pop(event.src_path, None)

    def call_back(self, event, full_path):
        rel_path = os.path.relpath(full_path, self.root_folder)
        self._call_back(event, rel_path, time.time())

    def on_created(self, event):
        if isinstance(event, FileCreatedEvent):
            self.logger.debug(
                "EventHandler: creation detected: {}".format(event.src_path)
            )
            if IS_MAC:
                if not event.src_path.endswith(".inwrite"):
                    self.call_back(CREATED_EVENT, event.src_path)
            else:
                # on linux two events are fired for a created file: first a
                # CREATED_EVENT and finally a MODIFIED_EVENT when the data is written to
                # disk.  but sometimes two CREATED_EVENT are fired but no
                # MODIFIED_EVENT. to handle this we record hashes of the file contents.
                with self.hash_lock:
                    hash_ = self.compute_hash(event)
                    if hash_ is not None and self.hash_changed(event, hash_):
                        self.update_hash(event, hash_)
                        self.call_back(CREATED_EVENT, event.src_path)

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent):
            self.logger.debug(
                "EventHandler: modification detected: {}".format(event.src_path)
            )
            if not event.src_path.endswith(".inwrite"):
                with self.hash_lock:
                    # read comments in on_created method !
                    hash_ = self.compute_hash(event)
                    if hash_ is not None and self.hash_changed(event, hash_):
                        self.update_hash(event, hash_)
                        self.call_back(MODIFIED_EVENT, event.src_path)

    def on_moved(self, event):
        """moving a file within the landing zone is disallowed"""
        if IS_MAC:
            self.call_back(ILLEGAL_EVENT, event.dest_path)
        else:
            self.call_back(CREATED_EVENT, event.dest_path)

    def on_deleted(self, event):
        """removing a file from the landing zone is disallowed"""
        self.remove_hash(event)
        self.call_back(ILLEGAL_EVENT, event.src_path)


def start_observer(folder, call_back, schedule_old_files=True):
    from datapool.logger import logger

    logger().info("start to observe {}".format(folder))
    from watchdog.observers import Observer

    event_handler = _EventHandler(folder, call_back, logger())
    observer = Observer()
    observer.schedule(event_handler, folder, recursive=True)
    observer.start()

    logger().info("started observer".format(folder))

    if schedule_old_files:
        for path in glob.glob(os.path.join(folder, "**/*.raw"), recursive=True):
            event_handler.on_created(FileCreatedEvent(path))
    return observer


def shutdown_observer(observer):
    from datapool.logger import logger

    logger().info("try to stop observer")
    observer.stop()
    observer.join()
    logger().info("stopped observer")


class Observer:
    def __init__(self, root_folder, call_back):
        self.root_folder = root_folder
        self.call_back = call_back
        self.observer_thread = None
        self.e = None

    def start(self, schedule_old_files=True):
        self.observer_thread = Thread(
            target=self._run_observer, args=(schedule_old_files,)
        )
        self.observer_thread.start()
        time.sleep(0.1)
        if self.e is not None:
            raise self.e from None

    def _run_observer(self, schedule_old_files):
        try:
            self._observer = start_observer(
                self.root_folder, self.call_back, schedule_old_files
            )
        except Exception as e:
            self.e = e

    def stop(self):
        shutdown_observer(self._observer)
        self.observer_thread.join()
