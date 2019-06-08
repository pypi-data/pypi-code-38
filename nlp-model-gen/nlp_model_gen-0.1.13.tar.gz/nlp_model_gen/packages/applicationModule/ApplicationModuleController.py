# @Classes
from nlp_model_gen.utils.classUtills import Singleton
from nlp_model_gen.packages.modelManager.ModelManagerController import ModelManagerController
from nlp_model_gen.packages.trainingModule.ModelTrainingController import ModelTrainingController
from .dataSanitizer.DataSanitizer import DataSanitizer

class ApplicationModuleController(metaclass=Singleton):
    def __init__(self):
        self.__model_manager = ModelManagerController()
        self.__model_trainer = ModelTrainingController()

    def analyse_text(self, model_id, text, only_positives=False):
        """
        Analiza un texto aplicandole el modelo solicitado. El modelo debe existir.

        :model_id: [String] - Id del modelo a utilizar.

        :text: [String] - Texto a analizar.

        :only_positives: [boolean] - Si esta activado, devuelve solo los resultados positivos.

        :return: [List(Dict)] - Resultados del analisis, None si ha ocurrido un error.
        """
        sanitized_text = DataSanitizer.sanitize_text_for_analysis(text)
        return self.__model_manager.analyze_text(model_id, sanitized_text, only_positives)

    def submit_training_example(self, model_id, example):
        """
        Provee de un ejemplo de entrenamiento. El mismo será agregado al sistema si cumple con 
        las validaciones de schema.

        :model_id: [String] - Id del modelo para el cual se provee el ejemplo.

        :example: [Dict] - Ejemplo de enetranamiento, se trata de un diccionario con dos partes:
        una oración y un arreglo que contiene entidades y su posición en la oración.
        """
        self.__model_trainer.add_training_examples(model_id, [example])

    def get_available_tagging_entities(self):
        """
        Devuelve el listado de la entidades disponibles para etiquetar entidades en los ejemplos
        de entrenamiento.

        :return: [List(Dict)] - Lista con todas las entidades posibles.
        """
        available_entities_list = list([])
        available_entities = self.__model_trainer.get_available_entities()
        for entity in available_entities:
            available_entities_list.append(entity.to_dict())
        return available_entities_list
