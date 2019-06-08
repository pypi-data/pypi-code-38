# @Vendors
import time

# @Error handler
from nlp_model_gen.packages.errorHandler.ErrorHandler import ErrorHandler

# @Constants
from nlp_model_gen.constants.constants import (
    TASK_KEYS_MODEL_UPDATE,
    TASK_KEYS_WORD_PROCESSOR,
    TOKENIZER_RESULTS_PLACEHOLDER
)

# @Utils
from nlp_model_gen.utils.fileUtils import get_file_name, validate_file

# @Classes
from nlp_model_gen.utils.classUtills import Observer
from nlp_model_gen.packages.adminModule.AdminModuleController import AdminModuleController
from ..task.Task import Task
from ..textAnalysisTask.TextAnalysisTask import TextAnalysisTask

class FilesAnalysisTask(Task, Observer):
    def __init__(self, id, model_id, files, only_positives):
        super(FilesAnalysisTask, self).__init__(id, {TASK_KEYS_MODEL_UPDATE: False, TASK_KEYS_WORD_PROCESSOR: True})
        Observer.__init__(self)
        self.__model_id = model_id
        self.__files = files
        self.__only_positives = only_positives
        self.__analysis_tasks = list([])
        self.__completed_tasks = 0

    def get_model_id(self):
        return self.__model_id

    def get_files(self):
        files_data = list([])
        for file in self.__files:
            files_data.append(file.name)
        return files_data

    def is_only_positives(self):
        return self.__only_positives

    def update(self, data):
        """
        Escucha cada una de las subtareas de analysis para controlar la finalización de
        las mismas.
        """
        self.__completed_tasks = self.__completed_tasks + 1

    def __check_task_finalized(self):
        return len(self.__analysis_tasks) == self.__completed_tasks

    def __build_results(self):
        results = list([])
        for task in self.__analysis_tasks:
            task_status = task['task'].get_task_status_data()
            task_results = dict({})
            task_results['file'] = task['file']
            task_results['error'] = task_status['error']
            task_results['success'] = not task_results['error']['active']
            task_results['findings'] = task_status['results'] if task_results['success'] else TOKENIZER_RESULTS_PLACEHOLDER
            results.append(task_results)
        return results

    def check_model_relation(self, model_id, model_name):
        """
        Determina si una tarea esta relacionada con un determinado modelo utilizando su
        id y su nombre

        :model_id: [String] - Id del modelo

        :model_name: [String] - Nombre del modelo

        :return: [boolean] - True si el modelo esta releacionado, False en caso contrario.
        """
        return model_id == self.__model_id

    def task_init_hook(self):
        """
        Método hook para completar el template de inicializadion en el padre.
        """
        try:
            adminModule = AdminModuleController()
            adminModule.load_model(self.__model_id)
            for file in self.__files:
                if not validate_file(file):
                    ErrorHandler.raise_error('E-0096')
                file_text = file.read()
                analysis_task = TextAnalysisTask(-1, self.__model_id, file_text, self.__only_positives)
                analysis_task.add_observer(self)
                self.__analysis_tasks.append({'file': get_file_name(file), 'task': analysis_task})
                analysis_task.init()
            while not self.__check_task_finalized():
                time.sleep(5)
            self.set_results(self.__build_results())
        except Exception as e:
            error = ErrorHandler.get_error_dict(e)
            self.set_error_data(error)

    def get_task_data(self):
        """
        Retorna los datos de la tarea.

        :return: [Dict] - Diccionario con los datos de la tarea.
        """
        return {
            'model_id': self.get_model_id(),
            'text': self.get_text(),
            'only_positives': self.is_only_positives()
        }
    