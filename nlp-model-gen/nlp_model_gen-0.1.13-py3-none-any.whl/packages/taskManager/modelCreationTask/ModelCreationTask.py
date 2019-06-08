# @Error handler
from nlp_model_gen.packages.errorHandler.ErrorHandler import ErrorHandler

# @Constants
from nlp_model_gen.constants.constants import (
    TASK_KEYS_MODEL_UPDATE,
    TASK_KEYS_WORD_PROCESSOR
)

# @Classes
from nlp_model_gen.packages.adminModule.AdminModuleController import AdminModuleController
from ..task.Task import Task

class ModelCreationTask(Task):
    def __init__(self, id, model_id, model_name, description, author, tokenizer_exceptions, max_dist):
        super(ModelCreationTask, self).__init__(id, {TASK_KEYS_MODEL_UPDATE: False, TASK_KEYS_WORD_PROCESSOR: True})
        self.__model_id = model_id
        self.__model_name = model_name
        self.__description = description
        self.__author = author
        self.__tokenizer_exceptions = tokenizer_exceptions
        self.__max_dist = max_dist

    def get_model_id(self):
        return self.__model_id

    def get_model_name(self):
        return self.__model_name

    def get_description(self):
        return self.__description

    def get_author(self):
        return self.__author

    def get_tokenizer_exceptions(self):
        return self.__tokenizer_exceptions

    def check_model_relation(self, model_id, model_name):
        """
        Determina si una tarea esta relacionada con un determinado modelo utilizando su
        id y su nombre

        :model_id: [String] - Id del modelo

        :model_name: [String] - Nombre del modelo

        :return: [boolean] - True si el modelo esta releacionado, False en caso contrario.
        """
        return model_name == self.__model_name

    def task_init_hook(self):
        """
        Método hook para completar el template de inicializadion en el padre.
        """
        try:
            admin = AdminModuleController()
            admin.generate_model(self.__model_id, self.__model_name, self.__description, self.__author, self.__tokenizer_exceptions, self.__max_dist)
            self.set_results(self.get_task_data())
        except Exception as e:
            error = ErrorHandler.get_error_dict(e)
            self.set_error_data(error)

    def get_task_data(self):
        """
        Devuelve los datos de la tarea.

        :return: [Dict] - Diccionario con los datos de la tarea.
        """
        return {
            'model_id': self.get_model_id(),
            'model_name': self.get_model_name(),
            'description': self.get_description(),
            'author': self.get_author(),
            'tokenizer_exceptions': self.get_tokenizer_exceptions()
        }
