# @Logger
from nlp_model_gen.packages.logger.Logger import Logger

# @Error handler
from nlp_model_gen.packages.errorHandler.ErrorHandler import ErrorHandler

# @Constatns
from nlp_model_gen.constants.constants import (MODEL_MANAGER_DB, MODEL_MANAGER_MODELS_COLLECTION, ANALYZER_EXCEPTIONS_COLLECTION)

# @Helpers
from nlp_model_gen.utils.dbUtils import ( 
    db_delete_item,
    db_delete_items,
    db_get_items,
    db_insert_item,
    db_update_item
)

class ModelDataManager:
    def __init__(self):
        pass

    @staticmethod
    def get_models():
        """
        Devuelve un listado de los modelos disponibles y sus caracteristicas.

        :return: [List(Dict)] - Listado de todos los modelos y sus datos.
        """
        try:
            available_models = db_get_items(MODEL_MANAGER_DB, MODEL_MANAGER_MODELS_COLLECTION, None, {'_id': 0})
            return available_models
        except:
            return None

    @staticmethod
    def check_existing_model(model_id):
        """
        Devuelve un listado de los identificadores de cada modelo disponible.

        :model_id: [String] - id del modelo buscado. 

        :return: [Boolean] - True si se ha encontrado el modelo, False en caso contrario
        """
        available_model_names = list(map(
            lambda model: model['model_id'], 
            db_get_items(MODEL_MANAGER_DB, MODEL_MANAGER_MODELS_COLLECTION, None, {'model_id': 1})
        ))
        return model_id in available_model_names

    @staticmethod
    def save_model_data(model_id, model_name, description, author, path, analyser_rules_set):
        """
        Guarda información de un modelo.

        :model_id: [String] - Id del modelo.

        :model_name: [String] - Nombre del modelo (actua como id).

        :description: [String] - Descripción del modelo.

        :author: [String] - Nombre del creador del modelo.

        :path: [String] - Ruta relativa para encontrar el modelo.

        :analyser_rules_set: [List(Dict)] - Lista de reglas para el analizador
        """
        Logger.log('L-0026')
        if ModelDataManager.check_existing_model(model_id):
            ErrorHandler.raise_error('E-0029')
        data_dict = {
            'model_id': model_id,
            'model_name': model_name,
            'description': description,
            'author': author,
            'path': path,
            'analyzer_rules_set': analyser_rules_set
        }
        db_insert_item(MODEL_MANAGER_DB, MODEL_MANAGER_MODELS_COLLECTION, data_dict)
        Logger.log('L-0029')

    @staticmethod
    def modify_model_data(model_id, model_name, description):
        """
        Modifica el nombre o la descripción de un modelo, el nuevo nombre no debe existir y si debe hacerlo el previo.

        :model_id: [String] - Id del modelo.

        :model_name: [String] - Nuevo nombre del modelo.

        :description: [String] - Nueva descripción del modelo.
        """
        Logger.log('L-0080')
        updated_data = {
            'model_name': model_name,
            'description': description
        }
        update_count = db_update_item(MODEL_MANAGER_DB, MODEL_MANAGER_MODELS_COLLECTION, {'model_id': model_id}, updated_data).modified_count
        if update_count <= 0:
            ErrorHandler.raise_error('E-0076')

    @staticmethod
    def remove_model_data(model_id):
        """
        Elimina la entrada para un modelo.

        :model_id: [String] - Id del modelo a eliminar.
        """
        Logger.log('L-0066')
        model_delete_count = db_delete_item(MODEL_MANAGER_DB, MODEL_MANAGER_MODELS_COLLECTION, {'model_id': model_id}).deleted_count
        if model_delete_count <= 0:
            ErrorHandler.raise_error('E-0072')
        db_delete_items(MODEL_MANAGER_DB, ANALYZER_EXCEPTIONS_COLLECTION, {'model_id': model_id})

    @staticmethod
    def add_analyzer_exception(model_id, base_form, token_text, enabled=True):
        """
        Agrega a la base de datos una nueva excepción al analizador para un modelo particular.

        :model_id: [String] - Id del modelo.

        :base_form: [String] - Forma base del token de la excepción.

        :token_text: [String] - Texto particular del token a exceptuar.

        :enabled: [Boolean] - Estado de la excepción (True habilitada, False deshabilitada)
        """
        analyzer_exception = {
            'model_id': model_id,
            'base_form': base_form,
            'token_text': token_text,
            'enabled': enabled
        }
        db_insert_item(MODEL_MANAGER_DB, ANALYZER_EXCEPTIONS_COLLECTION, analyzer_exception)

    @staticmethod
    def enable_analyzer_exception(model_id, base_form, token_text):
        """
        Habilita una excepción del analizador en la base de datos.

        :model_id: [String] - Id del modelo.

        :base_form: [String] - Forma base del token de la excepción.

        :token_text: [String] - Texto particular del token a exceptuar.
        """
        update_count = db_update_item(
            MODEL_MANAGER_DB, 
            ANALYZER_EXCEPTIONS_COLLECTION, 
            {'model_id': model_id, 'base_form': base_form, 'token_text': token_text}, 
            {'enabled': True}
        ).modified_count
        if update_count <= 0:
            ErrorHandler.raise_error('E-0113')

    @staticmethod
    def disable_analyzer_exception(model_id, base_form, token_text):
        """
        Deshabilita una excepción del analizador en la base de datos.

        :model_id: [String] - Id del modelo.

        :base_form: [String] - Forma base del token de la excepción.

        :token_text: [String] - Texto particular del token a exceptuar.
        """
        update_count = db_update_item(
            MODEL_MANAGER_DB, 
            ANALYZER_EXCEPTIONS_COLLECTION, 
            {'model_id': model_id, 'base_form': base_form, 'token_text': token_text}, 
            {'enabled': False}
        ).modified_count
        if update_count <= 0:
            ErrorHandler.raise_error('E-0116')

    @staticmethod
    def get_analyzer_exceptions_data(model_id):
        """
        Obtiene la lista de excepciones para el analizador de un modelo.

        :model_id: [String] - Id del modelo.

        :return: [List] - Listado con las excepciones encontradas para el
        modelo solicitado
        """
        analyzer_exceptions = list(db_get_items(MODEL_MANAGER_DB, ANALYZER_EXCEPTIONS_COLLECTION, {'model_id': model_id}))
        return analyzer_exceptions
