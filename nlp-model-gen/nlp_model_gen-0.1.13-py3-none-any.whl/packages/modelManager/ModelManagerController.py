# @Logger
from nlp_model_gen.packages.logger.Logger import Logger

# @Error handler
from nlp_model_gen.packages.errorHandler.ErrorHandler import ErrorHandler

# @Utils
from nlp_model_gen.utils.fileUtils import get_files_in_dir, load_json_file

# @Config
from nlp_model_gen.base import REMOTE_MODEL_SOURCE

# @Contants
from nlp_model_gen.constants.constants import (
    EVENT_MODEL_CREATED, 
    EVENT_MODEL_DELETED,
    TOKEN_RULES_GEN_RULES_EXT
)

# @Log colors
from nlp_model_gen.packages.logger.assets.logColors import ERROR_COLOR

# @Classes
from nlp_model_gen.utils.classUtills import ObservableSingleton
from .modelDataManager.ModelDataManager import ModelDataManager
from .modelLoader.ModelLoader import ModelLoader
from .model.Model import Model

class ModelManagerController(ObservableSingleton):
    def __init__(self):
        ObservableSingleton.__init__(self)
        self.__models = list([])
        self.__init_success = False
        self.__initialize()

    def __initialize(self):
        """
        Inicializa el modulo.
        """
        try:
            Logger.log('L-0051')
            stored_models_data = ModelDataManager.get_models()
            for model in stored_models_data:
                model_object = Model(model['model_id'], model['model_name'], model['description'], model['author'], model['path'], model['analyzer_rules_set'], [])
                model_analyzer_exceptions = ModelDataManager.get_analyzer_exceptions_data(model['model_id'])
                for analyzer_exception in model_analyzer_exceptions:
                    model_object.add_analyzer_exception(analyzer_exception['base_form'], analyzer_exception['token_text'], analyzer_exception['enabled'])
                self.__models.append(model_object)
            Logger.log('L-0052')
            self.__init_success = True
        except Exception as e:
            self.__init_success = False
            ErrorHandler.raise_error('E-0021', [{'text': e, 'color': ERROR_COLOR}])

    def __initialize_custom_model(self):
        """
        Inicializa un nuevo modelo de spacy, cargando lo en memoria.

        :return: [SpacyModelRef] - Referencia al nuevo modelo de spacy creado.
        """
        return ModelLoader.initiate_default_model()

    def is_ready(self):
        return self.__init_success

    def get_model(self, model_id):
        """
        Obtiene un modelo de la lista de modelos disponibles.

        :model_id: [String] - Id del modelo.

        :return: [Model] - Modelo encontrado, None si el modelo no existe
        """
        for model in self.__models:
            if model.get_model_id() == model_id:
                return model
        return None

    def load_model(self, model_id):
        """
        Carga el modelo requerido en memoria.

        :model_id: [String] - Id del modelo.

        :return: [boolean] - True si fue exitoso, false en caso contrario.
        """
        selected_model = self.get_model(model_id)
        if selected_model is None:
            return False
        selected_model.load()
        return selected_model.is_loaded()

    def get_available_models(self):
        """
        Devuelve una lista de los modelos disponibles y sus caracteristicas.

        :return: [List(Model)] - Lista de los modelos disponibles y sus caracteristicas.
        """
        return self.__models

    def get_available_models_dict(self):
        """
        Devuelve la lista de modelos disponibles y sus caracteristicas convertidos a formato dict.
        
        :return: [List(Dict)] - Lista de los modelos disponibles y sus caracteristicas.
        """
        models_list = list([])
        for model in self.__models:
            models_list.append(model.to_dict())
        return models_list

    def analyze_text(self, model_id, text='', only_positives=False):
        """
        Analiza un texto con el modelo solicitado.

        :model_id: [String] - Id del modelo a utilizar.

        :text: [String] - Texto a analizar.

        :only_positives: [boolean] - Si se activa solo se devolveran los resultados positivos del 
        análisis.

        :return: [List(Dict)] - Resultados del análisis.
        """
        Logger.log('L-0054')
        selected_model = self.get_model(model_id)
        if selected_model is None:
            ErrorHandler.raise_error('E-0095')
        if not selected_model.is_loaded():
            selected_model.load()
        return selected_model.analyse_text(text, only_positives)

    def __apply_tokenizer_exceptions(self, model, tokenizer_exceptions_path):
        """
        Aplica todas las excepciones contenidas en el directorio de excepciones al modelo.

        :model: [SpacyModelRef] - Modelo sobre el cual aplicar las excepc¡ones.

        :tokenizer_exceptions_path: [String] - Ruta al directorio de excepciones para el modelo.
        """
        Logger.log('L-0023')
        tokenizer_exceptions_files = get_files_in_dir(tokenizer_exceptions_path, TOKEN_RULES_GEN_RULES_EXT)
        for source_file in tokenizer_exceptions_files:
            rule_set = load_json_file(source_file)
            for key in rule_set:
                model.add_tokenizer_rule_set(rule_set[key])
        Logger.log('L-0024')

    def __check_exception_existence(self, model, base_form, token_text):
        """
        Valida la existencia de una excepción al analizador de un modelo que cumpla con la
        combinación token_base / especifico provista.

        :model: [Model] - Modelo.

        :base_form: [String] - Forma base del token.

        :token_text: [String] - Forma especifica en la que detectar el token.

        :return: [boolean] - True si se ha detectado, False en caso contrari
        """
        return model.check_exception(base_form, token_text)

    def create_model(self, model_id, model_name, description, author, tokenizer_exceptions_path, analyzer_rule_set):
        """
        Crea un nuevo modelo. Crea los datos necesarios y lo guarda tanto en disco como su
        referencia en la base de datos.

        :model_id: [String] - Identificador del modelo (se usará también como path para buscar el modelo)

        :model_name: [String] - Nombre del modelo.

        :description: [String] - Descripción.

        :author: [String] - Referencia del autor del modelo.

        :tokenizer_exceptions_path: [List(Dict)] - Lista de excepciones del modulo tokenizer del modelo.

        :analyzer_rule_set: [List(Dict)] - Lista de reglas para el analizador.
        """
        Logger.log('L-0021')
        custom_model = self.__initialize_custom_model()
        new_model = Model(model_id, model_name, description, author, model_id, analyzer_rule_set, [])
        new_model.set_reference(custom_model)
        Logger.log('L-0022')
        self.__apply_tokenizer_exceptions(new_model, tokenizer_exceptions_path)
        ModelDataManager.save_model_data(model_id, model_name, description, author, model_id, analyzer_rule_set)
        ModelLoader.save_model(custom_model, model_id, tokenizer_exceptions_path, new_model)
        self.__models.append(new_model)
        Logger.log('L-0025')
        self.notify({'event': EVENT_MODEL_CREATED, 'payload': new_model})

    def edit_model(self, model_id, model_name, description):
        """
        Permite editar la descripción de un modelo. El modelo debe existir.

        :model_id: [String] - Id del modelo.

        :model_name: [String] - Nuevo nombre para el modelo.

        :description: [String] - Nueva descripción para el modelo.
        """
        selected_model = self.get_model(model_id)
        ModelDataManager.modify_model_data(model_id, model_name, description)
        selected_model.set_model_name(model_name)
        selected_model.set_description(description)
        Logger.log('L-0082')

    def remove_model(self, model_id):
        """
        Elimina un modelo del sistema. Borra los datos del mismo de la base de datos y elimina los archivos
        del mismo del disco.

        :model_id: [String] - Id del modelo.
        """
        Logger.log('L-0064')
        selected_model = self.get_model(model_id)
        if selected_model is None:
            ErrorHandler.raise_error('E-0071')
        ModelDataManager.remove_model_data(selected_model.get_model_id())
        Logger.log('L-0069')
        ModelLoader.delete_model_files(selected_model.get_path())
        Logger.log('L-0072')
        self.__models.remove(selected_model)
        self.notify({'event': EVENT_MODEL_DELETED, 'payload': model_id})
        Logger.log('L-0073')

    def add_analyzer_exception(self, model_id, base_form, token_text, enabled=True):
        """
        Agrega una excepción al analizador para un modelo particular.

        :model_id: [String] - Id del modelo.

        :base_form: [String] - Forma base del token.

        :token_text: [String] - Forma especifica en la que detectar el token.

        :enabled: [boolean] - True si esta habilitada, False en caso contrario (por defecto
        True)
        """
        Logger.log('L-0002')
        model = self.get_model(model_id)
        if not model:
            ErrorHandler.raise_error('E-0107')
        if self.__check_exception_existence(model, base_form, token_text):
            ErrorHandler.raise_error('E-0108')
        Logger.log('L-0013')
        ModelDataManager.add_analyzer_exception(model_id, base_form, token_text)
        Logger.log('L-0018')
        model.add_analyzer_exception(base_form, token_text, enabled)
        Logger.log('L-0019')

    def enable_analyzer_exception(self, model_id, base_form, token_text):
        """
        Habilita una excepción del analizador. La misma no debe estar habilitada
        previamente.

        :model_id: [String] - Id del modelo.

        :base_form: [String] - Forma base del token.

        :token_text: [String] - Forma especifica en la que detectar el token.
        """
        Logger.log('L-0020')
        model = self.get_model(model_id)
        if not model:
            ErrorHandler.raise_error('E-0111')
        analyzer_exception = model.find_exception(base_form, token_text)
        if not analyzer_exception or analyzer_exception.is_enabled():
            ErrorHandler.raise_error('E-0112')
        Logger.log('L-0058')
        ModelDataManager.enable_analyzer_exception(model_id, base_form, token_text)
        Logger.log('L-0060')
        analyzer_exception.enable()
        Logger.log('L-0067')

    def disable_analyzer_exception(self, model_id, base_form, token_text):
        """
        Deshabilita una excepción del analizador. La misma no debe estar habilitada
        previamente.

        :model_id: [String] - Id del modelo.

        :base_form: [String] - Forma base del token.

        :token_text: [String] - Forma especifica en la que detectar el token.
        """
        Logger.log('L-0071')
        model = self.get_model(model_id)
        if not model:
            ErrorHandler.raise_error('E-0114')
        analyzer_exception = model.find_exception(base_form, token_text)
        if not analyzer_exception or not analyzer_exception.is_enabled():
            ErrorHandler.raise_error('E-0115')
        Logger.log('L-0079')
        ModelDataManager.disable_analyzer_exception(model_id, base_form, token_text)
        Logger.log('L-0081')
        analyzer_exception.disable()
        Logger.log('L-0084')

    def get_analyzer_exceptions(self, model_id):
        """
        Obtiene un listado de todas las excepciones al analizador para un modelo
        particular.

        :model_id: [String] - Id del modelo.

        :return: [List(Dict)] - Lista con todas las excepciones existentes para el
        modelo y su detalle.
        """
        Logger.log('L-0094')
        model = self.get_model(model_id)
        if not model:
            ErrorHandler.raise_error('E-0110')
        analyzer_exceptions = list([])
        for found_exception in model.get_analyzer_exceptions_set():
            analyzer_exceptions.append(found_exception.to_dict())
        Logger.log('L-0098')
        return analyzer_exceptions

    def import_model(self, model_id, source=None):
        """
        Importa un modelo existente desde el repositorio de modelos. No debe existir
        un modelo local con dicho id y, además, el módelo debe existir en el repositorio
        remoto de modelos.

        :model_id: [String] - Id del modelo a importar.

        :source: [Dict] - Fuente de donde obtener el modelo, puede ser un repositorio
        git o un directorio local.
        """
        Logger.log('L-0116')
        model = self.get_model(model_id)
        if model:
            ErrorHandler.raise_error('E-0118')
        if not source:
            source = REMOTE_MODEL_SOURCE
        cfg = ModelLoader.import_model(model_id, source)
        analyzer_exceptions_set_data = cfg['analyzer_exceptions_set']
        Logger.log('L-0179')
        ModelDataManager.save_model_data(model_id, cfg['model_name'], cfg['description'], cfg['author'], model_id, cfg['analyzer_rules_set'])
        remote_model = Model(model_id, cfg['model_name'], cfg['description'], cfg['author'], model_id, cfg['analyzer_rules_set'], [])
        self.__models.append(remote_model)
        for exception in analyzer_exceptions_set_data:
            self.add_analyzer_exception(model_id, exception['base_form'], exception['token_text'], exception['enabled'])
        Logger.log('L-0188')
        Logger.log('L-0197')

    def export_model(self, model_id, output_path, split=True):
        """
        Empaqueta un modelo para ser exportado. El paquete se guardara en la ruta
        solicitada.

        :model_id: [String] - Id del modelo a exportar (debe existir)

        :output_path: [String] - Ruta absoluta a donde se desea guardar los datos
        del modelo.

        :split: [boolean] - Indica si se debe particionar el paquete del modelo.
        Cuando esta habilitada se particionará en paquetes de 20mb
        """
        Logger.log('L-0212')
        model = self.get_model(model_id)
        if not model:
            ErrorHandler.raise_error('E-0122')
        ModelLoader.export_model(model, output_path, split)
        Logger.log('L-0215')
