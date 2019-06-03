import logging
import urllib.request

import yaml
from fxq.core.beans.factory.annotation import Autowired
from fxq.core.stereotype import Repository

from fxq.geoffrey.config import ApplicationConfig
from fxq.geoffrey.model import Task

LOGGER = logging.getLogger("TaskRepository")


@Repository
class TaskRepository:

    @Autowired
    def __init__(self, application_config: ApplicationConfig):
        self.application_config = application_config
        self.tasks = {}
        LOGGER.info("Caching Tasks from %s" % self.application_config.get_config_uri())
        with urllib.request.urlopen(self.application_config.get_config_uri()) as ch:
            self.choices_yml = yaml.safe_load(ch)

        for section in self.choices_yml["choices"]["sections"]:
            section_name = section["section"]["name"]
            for task in section["section"]["tasks"]:
                task_name = task["task"]["name"]
                self.tasks[task["task"]["name"]] = Task(
                    section_name,
                    task_name,
                    True if task["task"]["default"] == 'y' else False,
                    task["task"]["script"]
                )

    def find_all(self):
        return self.tasks.values()

    def find_by_name(self, name):
        return self.tasks[name]

    def find_by_section(self, section):
        tasks = []
        for task in self.tasks.values():
            if task.section_name == section:
                tasks.append(task)

        return tasks
