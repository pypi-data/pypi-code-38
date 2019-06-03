from PyInquirer import style_from_dict, Token, Separator
from fxq.core.beans.factory.annotation import Autowired

from fxq.geoffrey.config import ApplicationConfig
from fxq.geoffrey.repository import TaskRepository
from fxq.geoffrey.runner import TaskRunner

style = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})


class GeoffreyCli:

    @Autowired
    def __init__(self, application_config, task_repository, task_runner):
        self.application_config: ApplicationConfig = application_config
        self.task_repository: TaskRepository = task_repository
        self.task_runner: TaskRunner = task_runner

    def task_exists(self, task_name):
        try:
            self.task_repository.find_by_name(task_name)
            return True
        except KeyError:
            return False

    def list_available_tasks(self):
        available_tasks = {}
        for task in self.task_repository.find_all():
            try:
                available_tasks[task.section_name].append(task.task_name)
            except KeyError:
                available_tasks[task.section_name] = [task.task_name]
        return available_tasks

    def get_choices(self):
        choices = []
        for section, tasks in self.list_available_tasks().items():
            choices.append(Separator(section))
            for task in tasks:
                choices.append({
                    'name': task,
                    'checked': self.task_repository.find_by_name(task).default
                })
        return choices

    def run_task(self, task_name):
        self.task_runner.run_task(self.task_repository.find_by_name(task_name))
