#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author    : Yang
# Creadted  : 2017-04-17 23:10:28

import os
import sys
import time
import subprocess
import signal
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def log(s):
    print "[Monitor] %s" % s

class PyChangeEventHandler(FileSystemEventHandler):
    def __init__(self, handler):
        super(PyChangeEventHandler, self).__init__()
        self.handler = handler
        self.last_handler = None

    def on_any_event(self, event):
        if self.last_handler and self.last_handler + 3 >= time.time():
            return
        if event.src_path.endswith(".go"):
            log("Go source file changed: %s" % event.src_path)
            self.handler()
            self.last_handler = time.time()


class WatchGo(object):
    def __init__(self, command, path, recursive=True):
        self.command = command
        self.path = path
        self.recursive = recursive
        self.process = None

    def start_process(self):
        log("Start process [%s]..." % ' '.join(self.command))
        self.process = subprocess.Popen(self.command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        log("Pid: %s" % self.process.pid)

    def kill_process(self):
        if self.process:
            log("Kill process [%s]..." % self.process.pid)
            try:
                parent = psutil.Process(self.process.pid)
            except psutil.NoSuchProcess:
                return
            children = parent.children(recursive=True)
            for pc in children:
                pc.send_signal(signal.SIGTERM)
            self.process = None

    def restart_process(self):
        self.kill_process()
        self.start_process()

    def start_watch(self):
        observer = Observer()
        observer.schedule(PyChangeEventHandler(self.restart_process), self.path, recursive=self.recursive)
        observer.start()
        log("Wathing directory %s..." % self.path)
        self.start_process()
        try:
            while True:
                time.sleep(0.5)
                if self.process.poll() == 0:
                    observer.stop()
                    break
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
