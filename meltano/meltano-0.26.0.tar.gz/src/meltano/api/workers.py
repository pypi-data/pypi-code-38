import logging
import threading
import time
import requests
import webbrowser
from colorama import Fore

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, EVENT_TYPE_MODIFIED

from meltano.core.project import Project
from meltano.core.plugin import Plugin
from meltano.core.config_service import ConfigService
from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.core.plugin_invoker import invoker_factory


class CompileEventHandler(PatternMatchingEventHandler):
    def __init__(self, compiler):
        self.compiler = compiler

        super().__init__(ignore_patterns=["*.m5oc"])

    def on_any_event(self, event):
        self.compiler.compile()


class MeltanoBackgroundCompiler:
    def __init__(self, project: Project, compiler: ProjectCompiler = None):
        self.project = project
        self.compiler = compiler or ProjectCompiler(project)
        self.observer = self.setup_observer()

    @property
    def model_dirs(self):
        return (self.project.root_dir("model"), self.project.model_dir())

    def setup_observer(self):
        event_handler = CompileEventHandler(self.compiler)
        observer = Observer()

        for source in self.model_dirs:
            observer.schedule(event_handler, str(source), recursive=True)

        return observer

    def start(self):
        try:
            self.observer.start()
            for source in self.model_dirs:
                logging.info(f"Auto-compiling models in '{str(source)}'")
        except OSError:
            # most probably INotify being full
            logging.warn(f"Model auto-compilation is disabled: INotify limit reached.")

    def stop(self):
        self.observer.stop()


class UIAvailableWorker(threading.Thread):
    def __init__(self, url, open_browser=False):
        super().__init__()

        self._terminate = False
        self.url = url
        self.open_browser = open_browser

    def run(self):
        while not self._terminate:
            try:
                response = requests.get(self.url)
                if response.status_code == 200:
                    print(f"{Fore.GREEN}Meltano is available at {self.url}{Fore.RESET}")
                    if self.open_browser:
                        webbrowser.open(self.url)
                    self._terminate = True

            except:
                pass

            time.sleep(2)

    def stop(self):
        self._terminate = True


class AirflowWorker(threading.Thread):
    def __init__(self, project: Project, airflow: Plugin = None):
        super().__init__()

        self.project = project
        self._plugin = airflow or ConfigService(project).get_plugin("airflow")

    def start_all(self):
        invoker = invoker_factory(self.project, self._plugin)
        self._webserver = invoker.invoke("webserver")
        self._scheduler = invoker.invoke("scheduler")

    def run(self):
        return self.start_all()

    def stop(self):
        self._webserver.terminate()
        self._scheduler.terminate()
