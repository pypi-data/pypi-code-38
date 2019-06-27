#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os
import time
import logging
from . import config
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import watchdog.events as events
from threading import Thread
from .cleepapi import CleepApi
from .file import File
from collections import deque

class ActionFileSync():
    def __init__(self, module=None):
        self.module = module

class ActionRestart():
    def __init__(self, frontend=False):
        self.frontend = frontend


class ActionsExecutor(Thread):
    """
    Actions executor
    Implements queue to execute sequentially actions
    """
    def __init__(self):
        Thread.__init__(self)
        Thread.daemon = True

        self.logger = logging.getLogger(self.__class__.__name__)
        self.running = True
        self.__queue = deque(maxlen=200)
        self.file = File()
        self.cleep = CleepApi()

    def stop(self):
        """
        Stop process
        """
        self.running = False

    def add_action(self, action):
        """
        Add an action to execute
        """
        self.__queue.appendleft(action)

    def __execute_action(self, action):
        """
        Execute specified action

        Args:
            action (dict): action to execute
        """
        if isinstance(action, ActionFileSync):
            if action.module is None:
                self.file.core_sync()
            else:
                self.file.module_sync(action.module)

        elif isinstance(action, ActionRestart):
            if action.frontend:
                self.cleep.restart_frontend()
            else:
                self.cleep.restart_backend()

    def run(self):
        """
        Main process: unqueue action and process it
        """
        while self.running:
            try:
                action = self.__queue.pop()
                self.__execute_action(action)

            except IndexError:
                #no action available
                time.sleep(0.25)

            except:
                #error occured during action execution
                self.logger.exception('Error during action execution:')


class CleepHandler(FileSystemEventHandler):
    """
    Watchdog handler for Cleep
    """
    REJECTED_FILENAMES = [
        u'4913', #vim furtive temp file to check user permissions
        u'.gitignore'
    ]
    REJECTED_EXTENSIONS = [
        u'.swp', #vim
        u'.swpx', #vim
        u'.swx', #vim
        u'.tmp', #generic?
        u'.offset', #pygtail
        u'.pyc', #python compiled
        u'.log' #log file
    ]
    REJECTED_PREFIXES = [
        u'.',
        u'~'
    ]
    REJECTED_SUFFIXES = [
        u'~'
    ]
    REJECTED_DIRS = [
        u'.git',
        u'.vscode',
        u'.editor'
    ]
    DEBOUNCE = 0.25 #seconds

    def __init__(self, actions_executor):
        self.__last_times = {
            'backend': 0,
            'frontend': 0
        }
        self.logger = logging.getLogger(self.__class__.__name__)
        self.actions_executor = actions_executor

    def __is_event_dropped(self, event):
        """
        Analyse event and return True if event must be dropped
        Return:
            bool: True if event must be dropped
        """
        #drop dir modified event or created file (that always comes with modified file)
        if type(event) in (events.DirModifiedEvent, events.FileCreatedEvent):
            self.logger.debug('Filtered: DirModifiedEvent or FileCreatedEvent')
            return True

        #filter invalid event
        if not event:
            self.logger.debug('Filtered: invalid event')
            return True

        #filter event on current script
        if event.src_path == u'.%s' % __file__:
            self.logger.debug('Filtered: event on current script')
            return True

        #filter root event
        if event.src_path == u'.':
            self.logger.debug('Filtered: root event')
            return True

        #filter invalid extension
        src_ext = os.path.splitext(event.src_path)[1]
        if src_ext in self.REJECTED_EXTENSIONS:
            self.logger.debug('Filtered: invalid extension')
            return True

        #filter by prefix
        for prefix in self.REJECTED_PREFIXES:
            if event.src_path.startswith(prefix):
                self.logger.debug('Filtered: source prefix')
                return True
            if getattr(event, u'dest_path', None) and event.dest_path.startswith(prefix):
                self.logger.debug('Filtered: destination prefix')
                return True

        #filter by suffix
        for suffix in self.REJECTED_SUFFIXES:
            if event.src_path.endswith(suffix):
                self.logger.debug('Filtered: source suffix')
                return True
            if getattr(event, u'dest_path', None) and event.dest_path.endswith(prefix):
                self.logger.debug('Filtered: destination suffix')
                return True

        #filter by filename
        for filename in self.REJECTED_FILENAMES:
            if event.src_path.endswith(filename):
                self.logger.debug('Filtered: filename')
                return True

        #filter by dir
        parts = event.src_path.split(os.path.sep)
        for dir in self.REJECTED_DIRS:
            if dir in parts:
                self.logger.debug('Filtered: directory')
                return True

        return False

    def __debounce(self, now, last_time):
        if now<(last_time+self.DEBOUNCE):
            return True
        return False

    def __change_on_module(self, event):
        """
        Change on module

        Args:
            event: watchdog event

        Returns:
            module name (string) or None if nothing found
        """
        pattern = '^%s/(.*?)/(?:frontend|backend|scripts)/.*$' % (config.MODULES_SRC)
        #self.logger.debug('Module pattern: %s' % pattern)

        if hasattr(event, 'src_path'):
            res = re.findall(pattern, event.src_path)
            if res and len(res)>0:
                return res[0]

        if hasattr(event, 'dest_path'):
            res = re.findall(pattern, event.dest_path)
            if res and len(res)>0:
                return res[0]
        
        return None

    def __change_on_core(self, event):
        """
        Change on core

        Args:
            event: watchdog event

        Returns:
            True if change occurs in core, False otherwise
        """
        pattern_core = '^(%s/(?!tests|modules)(.*\.py)|%s/.*)$' % (config.CORE_SRC, config.HTML_SRC)
        pattern_bin = '^%s/raspiot' % (config.BIN_SRC)
        #self.logger.debug('Core pattern: %s' % pattern_core)
        #self.logger.debug('Bin pattern: %s' % pattern_bin)

        if hasattr(event, 'src_path'):
            if re.search(pattern_core, event.src_path):
                return True
            if re.search(pattern_bin, event.src_path):
                return True

        if hasattr(event, 'dest_path'):
            if re.search(pattern_core, event.dest_path):
                return True

        return False

    def __change_on_frontend(self, event):
        """
        Detect change on frontend

        Args:
            event: watchdog event

        Returns:
            True if change on frontend, False otherwise
        """
        pattern = '^(%s/|%s/(?:.*?)/frontend/).*$' % (config.HTML_SRC, config.MODULES_SRC)
        #self.logger.debug('Frontend pattern: %s' % pattern)

        if hasattr(event, 'src_path'):
            res = re.search(pattern, event.src_path)
            if res:
                return True

        if hasattr(event, 'dest_path'):
            res = re.search(pattern, event.dest_path)
            if res:
                return True

        return False

    def on_any_event(self, event):
        try:
            now = time.time()
            self.logger.debug('Event: %s' % event)
            if not self.__is_event_dropped(event):
                self.__last_action_time = now

                #is event on backend or frontend ?
                frontend = self.__change_on_frontend(event)

                #debounce ?
                if self.__debounce(now, self.__last_times[('frontend' if frontend else 'backend')]):
                    self.logger.debug('  Dropped by debounce')
                    return 

                #is event on module ?
                change_on_core = False
                change_on_module = self.__change_on_module(event)
                if change_on_module is None:
                    change_on_core = self.__change_on_core(event)

                #push action and update last action time
                if change_on_module:
                    self.logger.debug('  Change on module "%s"' % change_on_module)
                    self.actions_executor.add_action(ActionFileSync(change_on_module))
                elif change_on_core:
                    self.logger.debug('  Change on core')
                    self.actions_executor.add_action(ActionFileSync())
                else:
                    self.logger.debug('  Dropped due to useless change')
                    return
                if frontend:
                    self.logger.debug('  Change on frontend')
                    self.actions_executor.add_action(ActionRestart(True))
                    self.__last_times['frontend'] = now
                else:
                    self.logger.debug('  Change on backend')
                    self.actions_executor.add_action(ActionRestart())
                    self.__last_times['backend'] = now

        except:
            self.logger.exception('Error occured during watcher event processing:')


class CleepWatchdog():
    """
    Cleep core and module watchdog
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.actions_executor = ActionsExecutor()

    def watch(self):
        """
        Start watchdog that monitors filesystem changes on Cleep sources
        """
        path = '%s/' % config.REPO_DIR
        self.actions_executor.start()

        if not os.path.exists(path):
            self.logger.error('Please get Cleep sources using "cleep-cli getcore" command')
            return False

        event_handler = CleepHandler(self.actions_executor)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        self.logger.info('Cleep watchdog is running on "%s" (CTRL-C to stop)' % path)
        observer.start()
        try:
            while True:
                time.sleep(0.25)
        except KeyboardInterrupt:
            observer.stop()
            self.actions_executor.stop()
        observer.join()

        return True

