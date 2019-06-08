# @Error handler
from nlp_model_gen.packages.errorHandler.ErrorHandler import ErrorHandler

# @Constants
from nlp_model_gen.constants.constants import (
    TASK_KEYS_MODEL_UPDATE,
    TASK_KEYS_WORD_PROCESSOR
)

# @Classes
from nlp_model_gen.packages.applicationModule.ApplicationModuleController import ApplicationModuleController
from nlp_model_gen.packages.modelManager.ModelManagerController import ModelManagerController
from ..task.Task import Task

class TextAnalysisTask(Task):
    def __init__(self, id, model_id, text, only_positives):
        super(TextAnalysisTask, self).__init__(id, {TASK_KEYS_MODEL_UPDATE: True, TASK_KEYS_WORD_PROCESSOR: False})
        self.__model_id = model_id
        self.__text = text
        self.__only_positives = only_positives

    def get_model_id(self):
        return self.__model_id

    def get_text(self):
        return self.__text

    def is_only_positives(self):
        return self.__only_positives

    def check_model_relation(self, model_id, model_name):
        """
        Determina si una tarea esta relacionada con un determinado modelo utilizando su
        id y su nombre

        :model_id: [String] - Id del modelo

        :model_name: [String] - Nombre del modelo

        :return: [boolean] - True si el modelo esta releacionado, False en caso contrario.
        """
        model_manager = ModelManagerController()
        model = model_manager.get_model(self.__model_id)
        return model_id == self.__model_id and not model.is_loaded()

    def task_init_hook(self):
        """
        Método hook para completar el template de inicializadion en el padre.
        """
        try:
            application_module = ApplicationModuleController()
            results = application_module.analyse_text(self.__model_id, self.__text, self.__only_positives)
            self.set_results(results)
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
    