# @Vendors
from abc import ABC, abstractmethod
import datetime
from threading import Thread

# @Logger
from nlp_model_gen.packages.logger.Logger import Logger

# Logger colors
from nlp_model_gen.packages.logger.assets.logColors import HIGHLIGHT_COLOR

# @Classes
from nlp_model_gen.utils.classUtills import Observable

# @Constants
from nlp_model_gen.constants.constants import (
    TASK_KEYS_MODEL_UPDATE,
    TASK_KEYS_WORD_PROCESSOR,
    TASK_STATUS_CANCELLED,
    TASK_STATUS_FINISHED,
    TASK_STATUS_QUEUED,
    TASK_STATUS_RUNNING
)

class Task(Thread, Observable, ABC):
    def __init__(self, id, blocking_data=None):
        Thread.__init__(self)
        Observable.__init__(self)
        self.__id = id
        self.__status = TASK_STATUS_QUEUED
        self.__error = {'active': False, 'code': '', 'description': ''}
        self.__init_time = -1
        self.__end_time = -1
        self.__results = None
        self.__blocking_data = blocking_data if blocking_data is not None else {TASK_KEYS_WORD_PROCESSOR: False, TASK_KEYS_MODEL_UPDATE: False}

    def get_id(self):
        return self.__id

    def get_status(self):
        return self.__status

    def get_error(self):
        return self.__error

    def get_init_time(self):
        return self.__init_time

    def get_end_time(self):
        return self.__end_time

    def get_results(self):
        return self.__results

    def is_blocking(self, task_keys):
        for key in task_keys:
            if self.__blocking_data[key]:
                return True
        return False

    def set_error_data(self, error):
        self.__error = {'active': True, 'description_data': error}

    def set_results(self, results):
        self.__results = results

    def run(self):
        """
        Inicia la ejecución del thread
        """
        Logger.log('L-0229', [{'text': self.__id, 'color': HIGHLIGHT_COLOR}])
        self.__init_time = datetime.datetime.now()
        self.__status = TASK_STATUS_RUNNING
        self.task_init_hook()
        self.__end_time = datetime.datetime.now()
        self.__status = TASK_STATUS_FINISHED
        self.notify(self)
        Logger.log('L-0230')

    def init(self):
        """
        Inicia la tarea.
        """
        if self.__status == TASK_STATUS_QUEUED:
            self.start()

    def abort(self):
        """
        Aborta la tarea. Su ejecución no debe haber iniciado para realizar esta operación.
        """
        if self.__status == TASK_STATUS_QUEUED:
            self.__status = TASK_STATUS_CANCELLED
            return True
        return False

    def get_task_status_data(self):
        """
        Retorna un resumen de la información de la tarea.

        :return: [Dict] - Diccionario con la inofrmación acerca del estdo de la tarea.
        """
        return {
            'id': self.get_id(),
            'status': self.get_status(),
            'init_time': self.get_init_time(),
            'end_time': self.get_end_time(),
            'error': self.get_error(),
            'results': self.get_results()
        }

    @abstractmethod
    def check_model_relation(self, model_id, model_name):
        """
        Determina si una tarea esta relacionada con un determinado modelo utilizando su
        id y su nombre

        :model_id: [String] - Id del modelo

        :model_name: [String] - Nombre del modelo

        :return: [boolean] - True si el modelo esta releacionado, False en caso contrario.
        """

    @abstractmethod
    def task_init_hook(self):
        """
        Método que se ejecutará en el template del init de la task de la clase padre.
        """

    @abstractmethod
    def get_task_data(self):
        """
        Retorna los datos de la tarea, debe ser sobreescrito por las subclases
        """
