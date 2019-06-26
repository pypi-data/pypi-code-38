import multiprocessing
import threading
from collections import OrderedDict

import psutil
from watchdog.events import RegexMatchingEventHandler
from watchdog.observers import Observer

from ievv_opensource.utils.logmixin import LogMixin


class WatchdogWatchConfig(object):
    """
    Used by plugins to configure watching.

    See :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.watch`.
    """
    def run(self):
        self.plugin.run()

    def __init__(self, watchfolders, watchregexes, plugin):
        """
        Args:
            watchfolders: List of folders to watch.
            watchregexes: List of regexes to watch.
            plugin: A :class:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin` object.
        """
        self.folders = watchfolders
        self.regexes = watchregexes
        self.plugin = plugin


class ProcessWrapper(object):
    def __init__(self, process):
        self.process = process
        self.process.daemon = True

    def start(self):
        self.process.start()

    def stop(self):
        try:
            process = psutil.Process(self.process.pid)
        except psutil.NoSuchProcess:
            pass
        else:
            for childprocess in process.children():
                childprocess.terminate()
            try:
                process.terminate()
            except psutil.NoSuchProcess:
                pass

    def join(self):
        self.process.join()


class ProcessWatchConfig(object):
    """

    """
    def __init__(self, plugin):
        """
        Args:
            plugin: A :class:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin` object.
        """
        self.plugin = plugin

    def create_process(self):
        process = multiprocessing.Process(target=self.plugin.run_watcher_process)
        return ProcessWrapper(process=process)


class WatchConfigPool(LogMixin):
    def __init__(self):
        self._watchconfigs = []

    def extend(self, watchconfigs):
        self._watchconfigs.extend(watchconfigs)

    def get_logger_name(self):
        return 'watcherpool'

    def __watch_folder(self, folderpath, plugins, regexes):
        event_handler = EventHandler(
            plugins=plugins,
            regexes=regexes
        )
        observer = Observer()
        observer.schedule(event_handler, folderpath, recursive=True)
        self.get_logger().info(
            'Starting watcher for folder {!r} with regexes {!r}. '
            'Runnables notified of changes: {}.'.format(
                folderpath, regexes, ', '.join(str(plugin) for plugin in plugins)))
        observer.start()
        return observer

    def __build_foldermap(self):
        # Note: We use OrderedDict here, and a list (instead of set) for
        #       plugins below to maintain the order of apps when building.
        #       This should not matter, but it is nice to have the apps
        #       build in the same order as they are listed in settings.
        watchdog_foldermap = OrderedDict()
        process_runnables = []
        for watchconfig in self._watchconfigs:
            if isinstance(watchconfig, WatchdogWatchConfig):
                for folderpath in watchconfig.folders:
                    if folderpath not in watchdog_foldermap:
                        watchdog_foldermap[folderpath] = {
                            'regexes': set(),
                            'plugins': []
                        }
                    watchdog_foldermap[folderpath]['regexes'].update(watchconfig.regexes)
                    if watchconfig.plugin not in watchdog_foldermap[folderpath]['plugins']:
                        watchdog_foldermap[folderpath]['plugins'].append(watchconfig.plugin)
            elif isinstance(watchconfig, ProcessWatchConfig):
                process_runnables.append(watchconfig)
            else:
                raise ValueError('Unknown watch config type: {}'.format(type(watchconfig)))
        return watchdog_foldermap, process_runnables

    def watch(self):
        watchdog_foldermap, process_runnables = self.__build_foldermap()
        observers = []
        for folderpath, folderkwargs in watchdog_foldermap.items():
            observer = self.__watch_folder(folderpath=folderpath, **folderkwargs)
            observers.append(observer)
        for process_runnable in process_runnables:
            process = process_runnable.create_process()
            process.start()
            observers.append(process)
        return observers


class EventHandler(RegexMatchingEventHandler):
    """
    Event handler for watchdog --- this is used by each watcher
    thread to react to changes in the filesystem.

    This is instantiated by :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.watch`
    to watch for changes in files matching
    :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.get_watch_regexes`
    in the folders specified in
    :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.get_watch_folders`.
    """
    def __init__(self, *args, **kwargs):
        self.plugins = kwargs.pop('plugins')
        self.runtimer = None
        self.is_running = False
        super(EventHandler, self).__init__(*args, **kwargs)

    def handle_plugin_run(self):
        if self.is_running:
            return
        self.is_running = True
        for plugin in self.plugins:
            plugin.runwrapper()

        self.is_running = False

    def on_any_event(self, event):
        if self.runtimer:
            self.runtimer.cancel()
        self.runtimer = threading.Timer(0.5, self.handle_plugin_run)
        self.runtimer.start()
