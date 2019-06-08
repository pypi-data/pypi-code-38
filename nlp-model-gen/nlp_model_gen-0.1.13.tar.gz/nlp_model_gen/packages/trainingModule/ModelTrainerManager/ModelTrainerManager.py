# @Logger
from nlp_model_gen.packages.logger.Logger import Logger

# @Error handler
from nlp_model_gen.packages.errorHandler.ErrorHandler import ErrorHandler

class ModelTrainerManager:
    def __init__(self):
        pass

    def __build_annotations(self, examples):
        """
        Crea el listado de ejemplos a partir de los ejemplos de entrenamiento.

        :examples: [List(TrainExample)] - Lista de ejemplos de entrenamiento.

        :return: [List] - Listado con la anotaciones.
        """
        Logger.log('L-0338')
        annotations = list([])
        for training_example in examples:
            annotations.append(training_example.get_annotations())
        Logger.log('L-0339')
        return annotations

    def train_model(self, model, examples):
        """
        Aplica un set de ejemplos de entrenamiento a un modelo.

        :model: [Model] - Id del modelo sobre el cual aplicar el set de ejemplos.

        :examples: [List] - Lista de ejemplos de entrenamiento
        """
        if not model:
            ErrorHandler.raise_error('E-0090')
        annotations = self.__build_annotations(examples)
        model.train_model(annotations)
        