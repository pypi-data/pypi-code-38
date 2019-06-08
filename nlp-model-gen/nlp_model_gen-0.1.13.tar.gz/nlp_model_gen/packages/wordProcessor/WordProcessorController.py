# @Vendors
import copy

# @Contants
from nlp_model_gen.constants.constants import (
    DB_OPERATION_DELETE,
    DB_OPERATION_DELETE_MANY,
    DB_OPERATION_INSERT,
    DB_OPERATION_INSERT_MANY,
    DB_OPERATION_UPDATE,
    WORD_PROCESSOR_CONFIG_DB,
    WORD_PROCESSOR_CONJ_CFG_COLLECTION,
    WORD_PROCESSOR_DEFAULT_CFG_OBJECT,
    WORD_PROCESSOR_DEFAULT_THEME,
    WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION,
    WORD_PROCESSOR_GENERAL_SETTING_COLLECTION,
    WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION,
    WORD_PROCESSOR_VERB_EXCEPTIONS_COLLECTION,
    WORD_PROCESSOR_VERB_GROUPS_COLLECTION,
    WORD_PROCESSOR_SCHEMAS
)

# @Logger
from nlp_model_gen.packages.logger.Logger import Logger

# @Error handler
from nlp_model_gen.packages.errorHandler.ErrorHandler import ErrorHandler

# @Logger colors
from nlp_model_gen.packages.logger.assets.logColors import ERROR_COLOR

# @Utils
from nlp_model_gen.utils.classUtills import Singleton
from nlp_model_gen.utils.fileUtils import load_dict_from_json
from nlp_model_gen.utils.objectUtils import (
    update_dict,
    remove_object_from_list
)
from nlp_model_gen.utils.dbUtils import (
    db_check_collection,
    db_delete_items,
    db_insert_item,
    db_get_items,
    db_get_item,
    db_drop_collection,
    db_batch_operation,
    db_update_item
)
from .packageUtils.validations import validate_config

# @Classes
from .spanishConjugator.Conjugator import Conjugator
from .spanishFuzzyTermsGenerator.FuzzyTermsGenerator import FuzzyTermsGenerator
from .spanishNounConversor.Conversor import Conversor

# @Configs
word_processor_default_cfg = load_dict_from_json('wordProcessor-default_config')

class WordProcessorController(metaclass=Singleton):
    """
    Controlador del modulo de procesamiento de palabras. Administra los modulos y 
    permite crear, modificar y establecer diferentes configuraciones para los modulos.

    Al iniciar se conecta a la base de datos para obtener tanto la configuración activa
    como los perfiles correspondientes a dicho tema.
    """
    def __init__(self, mode=0):
        Logger.log('L-0038')
        self.__init_success = False
        self.__conjugator_active_theme = ''
        self.__fuzzy_gen_active_theme = ''
        self.__noun_conversor_active_theme = ''
        self.__conjugator_general_cfg = dict({})
        self.__conjugator_verb_exceptions = list([])
        self.__conjugator_verb_groups = dict({})
        self.__fuzzy_generator_cfg = dict({})
        self.__noun_conversor_cfg = dict({})
        self.__initializate_cfg(mode)

    def __initializate_cfg(self, mode):
        """
        [private] Obtiene el tema de configuración activa para cada modulo y carga cada perfil
        de configuración.
        """
        try:
            self.__initialize_controller()
            self.__initialize_conjugator()
            self.__initialize_fuzzy_generator()
            self.__initialize_noun_conversor()
            self.__conjugator = Conjugator(mode, self.__conjugator_general_cfg, self.__conjugator_verb_groups, self.__conjugator_verb_exceptions)
            self.__fuzzy_generator = FuzzyTermsGenerator(self.__fuzzy_generator_cfg)
            self.__conversor = Conversor(self.__noun_conversor_cfg)
            Logger.log('L-0039')
            self.__init_success = True
        except Exception as e:
            self.__init_success = False
            ErrorHandler.raise_error('E-0020', [{'text': e, 'color': ERROR_COLOR}])

    def __initialize_controller(self):
        """
        [private] Inicializa el controlador cargando los perfiles de configuración activos
        para cada modulo.
        """
        Logger.log('L-0041')
        if not db_check_collection(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_GENERAL_SETTING_COLLECTION):
            db_insert_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_GENERAL_SETTING_COLLECTION, WORD_PROCESSOR_DEFAULT_CFG_OBJECT)
            self.__conjugator_active_theme = WORD_PROCESSOR_DEFAULT_CFG_OBJECT['conjugator_active_theme']
            self.__fuzzy_gen_active_theme = WORD_PROCESSOR_DEFAULT_CFG_OBJECT['fuzzy_gen_active_theme']
            self.__noun_conversor_active_theme = WORD_PROCESSOR_DEFAULT_CFG_OBJECT['noun_conversor_active_theme']
        else:
            db_data = db_get_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_GENERAL_SETTING_COLLECTION, None, {'_id': 0 })
            self.__conjugator_active_theme = db_data['conjugator_active_theme']
            self.__fuzzy_gen_active_theme = db_data['fuzzy_gen_active_theme']
            self.__noun_conversor_active_theme = db_data['noun_conversor_active_theme']
        Logger.log('L-0042')

    def __initialize_conjugator(self):
        """
        [private] Verifica si ya existen entradas para los perfiles de configuración en la 
        base de datos e inicializa el conjugador.

        Si no existen perfiles, carga el archivo de configuración por defecto y lo almacena en la 
        base de datos. En caso contrario, obtiene la configuración activa desde la base de datos.
        """
        Logger.log('L-0043')
        if not db_check_collection(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_CONJ_CFG_COLLECTION):
            self.__initialize_conjugator_cfg()
        else:
            self.__get_conjugator_cfg()
        Logger.log('L-0044')

    def __initialize_conjugator_cfg(self):
        """
        [private] Inicializa la configuración del conjugador cuando aun no hay entradas en la 
        base de datos. Obtiene los datos del archivo de configuración por defecto y 
        almacena las entradas.
        """
        db_drop_collection(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_CONJ_CFG_COLLECTION)
        db_drop_collection(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_VERB_EXCEPTIONS_COLLECTION)
        db_drop_collection(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_VERB_GROUPS_COLLECTION)
        conjugator_verb_exceptions = self.__generate_verb_exceptions()
        db_batch_operation(WORD_PROCESSOR_CONFIG_DB, [
            {'type': DB_OPERATION_INSERT, 'col_name': WORD_PROCESSOR_CONJ_CFG_COLLECTION, 'data': word_processor_default_cfg['conjugator_config']},
            {'type': DB_OPERATION_INSERT_MANY, 'col_name': WORD_PROCESSOR_VERB_EXCEPTIONS_COLLECTION, 'data': conjugator_verb_exceptions},
            {'type': DB_OPERATION_INSERT, 'col_name': WORD_PROCESSOR_VERB_GROUPS_COLLECTION, 'data': word_processor_default_cfg['conjugator_irregular_groups']}
        ])
        self.__conjugator_general_cfg = word_processor_default_cfg['conjugator_config']
        self.__conjugator_verb_exceptions = conjugator_verb_exceptions
        self.__conjugator_verb_groups = word_processor_default_cfg['conjugator_irregular_groups']

    def __generate_verb_exceptions(self):
        """
        [private] A partir de las excepciones almacenadas en el archivo de configuraciones por defecto
        crea una lista con todas las expceciones para insertar en la base de datos.

        :return: [List] - Lista de excepciones
        """
        verb_exceptions = list([])
        for verb_exception in word_processor_default_cfg['conjugator_verb_exceptions']['exceptions']:
            verb_exception['theme'] = WORD_PROCESSOR_DEFAULT_THEME
            verb_exceptions.append(verb_exception)
        return verb_exceptions

    def __get_conjugator_cfg(self):
        """
        [private] Obtiene las configuraciones del conjugador almacenadas en la base de datos para el
        tema activo.
        """
        self.__conjugator_general_cfg = db_get_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_CONJ_CFG_COLLECTION, {'theme': self.__conjugator_active_theme}, {'_id': 0, 'theme': 0})
        self.__conjugator_verb_exceptions = []
        for exception in db_get_items(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_VERB_EXCEPTIONS_COLLECTION, {'theme': self.__conjugator_active_theme}, {'_id': 0, 'theme': 0}):
            self.__conjugator_verb_exceptions.append(exception)
        self.__conjugator_verb_groups = db_get_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_VERB_GROUPS_COLLECTION, {'theme': self.__conjugator_active_theme}, {'_id': 0, 'theme': 0})

    def __initialize_fuzzy_generator(self):
        """
        [private] Verifica si existen entradas en la base de datos para el generador de terminos
        distorcionados. De existir obtiene las configuraciones de la base de datos. En caso
        contrario, almacena en la base de datos las configuraciones almacenadas en el archivo
        de configuración por defecto.
        """
        Logger.log('L-0045')
        if not db_check_collection(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION):
            self.__initialize_fuzzy_generator_cfg()
        else:
            self.__get_fuzzy_generator_cfg()
        Logger.log('L-0046')

    def __initialize_fuzzy_generator_cfg(self):
        """
        [private] A partir del archivo de configuraciones, inicializa la configuracion por defecto
        en la base de datos.
        """
        db_drop_collection(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION)
        db_insert_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION, word_processor_default_cfg['fuzzy_terms_generator_config'])
        self.__fuzzy_generator_cfg = word_processor_default_cfg['fuzzy_terms_generator_config']

    def __get_fuzzy_generator_cfg(self):
        """
        [private] Obtiene las configuraciones del generador de terminos distoricionados para
        el tema activo desde la base de datos
        """
        self.__fuzzy_generator_cfg = db_get_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION, {'theme': self.__fuzzy_gen_active_theme}, {'_id': 0, 'theme': 0})

    def __initialize_noun_conversor(self):
        """
        [private] Inicializa el conversor de sustantivos. Si ya existe la información en la base
        de datos, obtiene los datos para el tema activo desde la misma. En caso contario, obtiene
        la configuración por defecto del archivo de configuraciones y almacena las mismas
        en la base de datos
        """
        Logger.log('L-0047')
        if not db_check_collection(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION):
            self.__initialize_noun_conversor_cfg()
        else:
            self.__get_noun_conversor_cfg()
        Logger.log('L-0048')

    def __initialize_noun_conversor_cfg(self):
        """
        [private] Obtiene la configuración por defecto del conversor de sustantivos y hace el
        almacenamiento inicial de dicha configuración en la base de datos.
        """
        db_drop_collection(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION)
        db_insert_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION, word_processor_default_cfg['noun_conversor_config'])
        self.__noun_conversor_cfg = word_processor_default_cfg['noun_conversor_config']

    def __get_noun_conversor_cfg(self):
        """
        [private] Obtiene de la base de datos la configuración del conversor de sustantivos para
        el tema activo.
        """
        self.__noun_conversor_cfg = db_get_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION, {'theme': self.__noun_conversor_active_theme}, {'_id': 0, 'theme': 0})

    # *************************************************************************************    
    # Getters
    # *************************************************************************************

    def is_ready(self):
        return self.__init_success

    def get_conjugator_active_theme(self):
        return self.__conjugator_active_theme

    def get_fuzzy_gen_active_theme(self):
        return self.__fuzzy_gen_active_theme

    def get_noun_converseor_active_theme(self):
        return self.__noun_conversor_active_theme

    # *************************************************************************************

    def retry_initialization(self, mode=0):
        """
        Reintenta la inicialización del controlador.
        """
        self.__initializate_cfg(mode)

    def get_conjugator_configs(self):
        """
        Devuelve la configuración activa del conjugador.

        :return: [Dict] - Objeto de configuración general activa del conjugador.
        """
        return self.__conjugator_general_cfg

    def get_conjugator_exceptions(self):
        """
        Devuelve el conjunto de excepciones activas para el conjugador.

        :return: [List(Dict)] - Lista de excepciones activa del conjugador.
        """
        return self.__conjugator_verb_exceptions

    def get_conjugator_irr_groups(self):
        """
        Devuelve la configuración de grupos irregulares activa para el conjugador.

        :return: [Dict] - Lista de grupos irregulares activa del conjugador. 
        """
        return self.__conjugator_verb_groups

    def get_noun_conversor_configs(self):
        """
        Devuelve la configuración activa para el conversor de sustantivos.

        :return: [Dict] - Objeto de configuración activa del conversor de sustantivos.
        """
        return self.__noun_conversor_cfg

    def get_fuzzy_generator_configs(self):
        """
        Devuelve la configuración activa para el generador fuzzy.

        :return: [Dict] - Objeto de configuración activa del generador fuzzy.
        """
        return self.__fuzzy_generator_cfg

    def map_conjugator_exception(self, exception):
        """
        Mapea el nombre del theme en una excepción

        :exception: [Dict] - Objeto con los datos de la excepción

        :return: [Dict] - Clon del objeto original con el theme name agregado.
        """
        exception_copy = copy.deepcopy(exception)
        del exception_copy['theme']
        return exception_copy

    def filter_theme_exceptions(self, theme_name, exception_list=None):
        """
        Filtra las excepciones correspondientes a un determinado theme de una lista de excepciones.

        :theme_name: [String] - Nombre del tema.

        :exception_list: [List(Dict)] - Lista de excepciones.

        :return: [List(Dict)] - Lista de excepciones filtradas.
        """
        if exception_list is not None:
            filtered_exceptions_list = copy.deepcopy(list(exception_list))
        else:
            filtered_exceptions_list = []
        filtered_exceptions_list = list(filter(lambda exception: exception['theme'] == theme_name, filtered_exceptions_list))
        return list(map(self.map_conjugator_exception, filtered_exceptions_list))

    def get_available_conjugator_configs(self):
        """
        Devuelve todas las configuraciones disponibles para el conjugador

        :return: [List(Dict)] - Lista con todos temas de configuración disponibles.
        """
        try:
            Logger.log('L-0100')
            available_configs = db_get_items(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_CONJ_CFG_COLLECTION, fields={'_id': 0})
            available_exceptions = db_get_items(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_VERB_EXCEPTIONS_COLLECTION, fields={'_id': 0})
            available_irr_groups = db_get_items(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_VERB_GROUPS_COLLECTION, fields={'_id': 0})
            Logger.log('L-0101')
            Logger.log('L-0102')
            available_config_themes = []
            for config_theme in available_configs:
                theme_name = config_theme['theme']
                theme = dict({})
                theme['theme'] = theme_name
                theme['general_settings'] = config_theme
                theme['irregular_verb_exceptions'] = self.filter_theme_exceptions(theme_name, available_exceptions)
                theme['irregular_verb_groups'] = dict(next((group for group in available_irr_groups if group['theme'] == theme_name), {}))
                del theme['general_settings']['theme']
                del theme['irregular_verb_groups']['theme']
                available_config_themes.append(theme)
            Logger.log('L-0103')
            return available_config_themes
        except Exception as e:
            Logger.log('L-0104', [{'text': e, 'color': ERROR_COLOR}])
            return []

    def get_available_fuzzy_gen_configs(self):
        """
        Devuelve todas las configuraciones disponibles para el generador de terminos Fuzzy.

        :return: [List(Dict)] - Lista con todos los temas de configuración disponibles.
        """
        try:
            Logger.log('L-0105')
            available_configs = db_get_items(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION, fields={'_id': 0})
            Logger.log('L-0106')
            return available_configs
        except Exception as e:
            Logger.log('L-0107', [{'text': e, 'color': ERROR_COLOR}])
            return []

    def get_available_conversor_configs(self):
        """
        Devuelve todas las configuraciones disponibles para el conversor de sustantivos.

        :return: [List(Dict)] - Lista con todos los temas de configuración disponibles.
        """
        try:
            Logger.log('L-0108')
            available_configs = db_get_items(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION, fields={'_id': 0})
            Logger.log('L-0109')
            return available_configs
        except Exception as e:
            Logger.log('L-0110', [{'text': e, 'color': ERROR_COLOR}])
            return []

    def __get_existing_themes(self, collection_name):
        """
        Obtiene todos los themes disponibles dentro de una collección de la base de datos

        :collection_name: Nombre de la colección de la base de datos donde buscar los temás disponibles

        :return: [List(String)] - Lista con los nombres de todos los temas disponibles.
        """
        return list(map(lambda theme: theme['theme'], db_get_items(WORD_PROCESSOR_CONFIG_DB, collection_name, fields={'_id': 0, 'theme': 1})))

    def add_conjugator_config(self, theme_name, theme_config, theme_irregular_groups):
        """
        Agrega un nuevo tema de configuración general y grupos de verbos irregulares a la base de datos.
        El nuevo tema no debe existir.

        :theme_name: [String] - Nombre del tema.

        :theme_config: [Dict] - Objeto de configuración con el nuevo tema de configuración general. Debe 
        validar con la schema de validación correspondiente.

        :theme_irregular_groups: [Dict] - Objeto de configuración con el la configuración de grupos irregulares
        para el nuevo tema. Debe validar con la schema de validación correspondiente.
        """
        Logger.log('L-0111')
        existing_theme = theme_name in self.__get_existing_themes(WORD_PROCESSOR_CONJ_CFG_COLLECTION)
        if existing_theme:
            ErrorHandler.raise_error('E-0064')
        if not validate_config(WORD_PROCESSOR_SCHEMAS['CONJ_GENERAL_CFG'], theme_config) or not validate_config(WORD_PROCESSOR_SCHEMAS['CONJ_IRR_GROUPS'], theme_irregular_groups):
            ErrorHandler.raise_error('E-0065')
        Logger.log('L-0113')
        Logger.log('L-0114')
        updated_theme_config = copy.deepcopy(theme_config)
        updated_irregular_groups = copy.deepcopy(theme_irregular_groups)
        updated_theme_config['theme'] = theme_name
        updated_irregular_groups['theme'] = theme_name
        db_batch_operation(WORD_PROCESSOR_CONFIG_DB, [
            {'type': DB_OPERATION_INSERT, 'col_name': WORD_PROCESSOR_CONJ_CFG_COLLECTION, 'data': updated_theme_config},
            {'type': DB_OPERATION_INSERT, 'col_name': WORD_PROCESSOR_VERB_GROUPS_COLLECTION, 'data': updated_irregular_groups}
        ])
        Logger.log('L-0115')

    def add_conjugator_exceptions(self, theme_name, exceptions):
        """
        Agrega un conjunto de excepciones nuevo para el conjugador a la base de datos para el theme indicado.
        El theme debe existir.

        :theme_name: [String] - Nombre del tema.

        :exceptions: [List(Dict)] - Arreglo de excepciones a registrar. Debe cumplir con la schema de validación.
        """
        Logger.log('L-0117')
        if theme_name == WORD_PROCESSOR_DEFAULT_THEME or not theme_name in self.__get_existing_themes(WORD_PROCESSOR_CONJ_CFG_COLLECTION):
            ErrorHandler.raise_error('E-0059')
        Logger.log('L-0119')
        Logger.log('L-0120')
        transaction_data = []
        for exception in exceptions:
            if not validate_config(WORD_PROCESSOR_SCHEMAS['CONJ_EXCEPTIONS'], exception):
                ErrorHandler.raise_error('E-0060')
            if self.__check_exception_existence(theme_name, exception['key']):
                ErrorHandler.raise_error('E-0061')
            updated_exception = copy.deepcopy(exception)
            updated_exception['theme'] = theme_name
            transaction_data.append({'type': DB_OPERATION_INSERT, 'col_name': WORD_PROCESSOR_VERB_EXCEPTIONS_COLLECTION, 'data': updated_exception})
        Logger.log('L-0123')
        Logger.log('L-0124')
        db_batch_operation(WORD_PROCESSOR_CONFIG_DB, transaction_data)
        Logger.log('L-0125')
        if theme_name == self.__conjugator_active_theme:
            Logger.log('L-0126')
            updated_exceptions = self.get_conjugator_exceptions()
            updated_exceptions.extend(exceptions)
            self.__conjugator_verb_exceptions = updated_exceptions
            self.__conjugator.set_irregular_verb_exceptions_config(self.__conjugator_verb_exceptions)
            Logger.log('L-0127')

    def add_fuzzy_gen_config(self, theme_name, config):
        """
        Agrega un nuevo theme de configuración para el generador fuzzy. No debe existir un theme con el nombre indicado
        registrado.

        :theme_name: [String] - Nombre del theme a agregar

        :config: [Dict] - Objeto de configuración para el nuevo theme. Debe cumplir con la schema de validación
        """
        Logger.log('L-0129')
        existing_theme = theme_name in self.__get_existing_themes(WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION)
        if existing_theme:
            ErrorHandler.raise_error('E-0066')
        if not validate_config(WORD_PROCESSOR_SCHEMAS['FUZZY_GENERAL_CFG'], config):
            ErrorHandler.raise_error('E-0067')
        Logger.log('L-0131')
        Logger.log('L-0132')
        updated_config = copy.deepcopy(config)
        updated_config['theme'] = theme_name
        db_insert_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION, updated_config)
        Logger.log('L-0133')

    def add_noun_conversor_config(self, theme_name, config):
        """
        Agrega un nuevo theme de configuración para el conversor de sustantivos. No debe existir un theme con el nombre
        indicado previamente registrado.

        :theme_name: [String] - Nombre del theme a agregar

        :config: [Dict] - Objeto de cponfiguración para el nuevo theme. Debe cumplir con la schema de validación.
        """
        Logger.log('L-0135')
        existing_theme = theme_name in self.__get_existing_themes(WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION)
        if existing_theme:
            ErrorHandler.raise_error('E-0068')
        if not validate_config(WORD_PROCESSOR_SCHEMAS['NOUN_CONV_GENERAL_CFG'], config):
            ErrorHandler.raise_error('E-0069')
        Logger.log('L-0137')
        Logger.log('L-0138')
        updated_config = copy.deepcopy(config)
        updated_config['theme'] = theme_name
        db_insert_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION, updated_config)
        Logger.log('L-0139')

    def __get_theme_data(self, theme_name, collection_name):
        """
        [Private] Obtiene los datos de configuración para un tema en particular en la colleción indicada.

        :theme_name: [String] - Nombre del tema a buscar.

        :collection_name: [String] - Nombre de la colección en la cual buscar

        :return: [Dict] - Objeto de configuración
        """
        theme_data = db_get_item(WORD_PROCESSOR_CONFIG_DB, collection_name, {'theme': theme_name}, {'_id': 0, 'theme': 0})
        return theme_data

    def update_conjugator_configs(self, theme_name, theme_config_mod, theme_irr_groups_mod):
        """
        Modifica la configuración y los grupos irregulares para un tema determinado. El tema a editar debe existir, 
        no se puede modificar el tema por defecto.

        :theme_name: [String] - Nombre del tema a editar

        :theme_config_mod: [Dict] - Objeto con los campos a actualizar de la configuración. Los campos que se editen 
        sobre el tema seleccionado deben cumplir con la schema de validación.

        :theme_irr_groups_mod: [Dict] - Objeto con los campos a actualizar de los grupos de verbos irregulares. Los 
        campos que se editen sobre el tema seleccionado deben cumplir con la schema de validación.
        """
        Logger.log('L-0162')
        config_data = self.__get_theme_data(theme_name, WORD_PROCESSOR_CONJ_CFG_COLLECTION)
        irr_groups_data = self.__get_theme_data(theme_name, WORD_PROCESSOR_VERB_GROUPS_COLLECTION)
        if theme_name == WORD_PROCESSOR_DEFAULT_THEME or config_data is None or irr_groups_data is None:
            ErrorHandler.raise_error('E-0050')
        updated_config_data = update_dict(config_data, theme_config_mod, ['theme'])
        updated_irr_groups_data = update_dict(irr_groups_data, theme_irr_groups_mod, ['theme'])
        if not validate_config(WORD_PROCESSOR_SCHEMAS['CONJ_GENERAL_CFG'], updated_config_data) or not validate_config(WORD_PROCESSOR_SCHEMAS['CONJ_IRR_GROUPS'], updated_irr_groups_data):
            ErrorHandler.raise_error('E-0051')
        Logger.log('L-0165')
        Logger.log('L-0166')
        db_batch_operation(WORD_PROCESSOR_CONFIG_DB, [
            {'type': DB_OPERATION_UPDATE, 'col_name': WORD_PROCESSOR_CONJ_CFG_COLLECTION, 'data': updated_config_data, 'query': {'theme': theme_name}},
            {'type': DB_OPERATION_UPDATE, 'col_name': WORD_PROCESSOR_VERB_GROUPS_COLLECTION, 'data': updated_irr_groups_data, 'query': {'theme': theme_name}}
        ])
        Logger.log('L-0167')
        if theme_name == self.__conjugator_active_theme:
            Logger.log('L-0168')
            self.__conjugator_general_cfg = updated_config_data
            self.__conjugator_verb_groups = updated_irr_groups_data
            self.__conjugator.set_general_config(updated_config_data)
            self.__conjugator.set_irregular_verb_groups_config(updated_irr_groups_data)
            Logger.log('L-0169')

    def __check_exception_existence(self, theme_name, exception_key):
        """
        Valida que una excepción exista, en caso contrario devuelve false.

        :theme_name: [String] - Nombre del tema.

        :exception_key: [String] - Key de la excepción.

        :return: [Boolean] - True si la excepción existe, False en caso contrario.
        """
        exception_data = db_get_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_VERB_EXCEPTIONS_COLLECTION, {'theme': theme_name, 'key': exception_key}, {'_id': 0})
        return exception_data is not None

    def update_conjugator_exception(self, theme_name, exception_key, exception_new_data):
        """
        Actualiza una excepción del conjunto de excepciones del conjugador para un tema. La key y el tema deben existir.
        No se pueden editar excepciones del tema por defecto. La excepción debe complir con la schema de validación.
        Por las caracteristicas de la excepción, se requiere que se provea el objeto completo y no solo los campos a
        modificar.

        :theme_name: [String] - Nombre del tema.

        :exception_key: [String] - Key o verbo del cual se eliminará la excepción.

        :exception_new_data: [Dict] - Datos actualizados de la excepción.
        """
        Logger.log('L-0189')
        if not self.__check_exception_existence(theme_name, exception_key) or theme_name == WORD_PROCESSOR_DEFAULT_THEME:
            ErrorHandler.raise_error('E-0046')
        updated_exception_data = update_dict(exception_new_data, {'key': exception_key})
        if not validate_config(WORD_PROCESSOR_SCHEMAS['CONJ_EXCEPTIONS'], updated_exception_data):
            ErrorHandler.raise_error('E-0047')
        Logger.log('L-0192')
        Logger.log('L-0193')
        updated_exception_data['theme'] = theme_name
        updated_entries = db_update_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_VERB_EXCEPTIONS_COLLECTION, {'theme': theme_name, 'key': exception_key}, updated_exception_data).matched_count
        if updated_entries <= 0:
            ErrorHandler.raise_error('E-0048')
        Logger.log('L-0194')
        if theme_name == self.__conjugator_active_theme:
            Logger.log('L-0195')
            remove_object_from_list(self.__conjugator_verb_exceptions, {'theme': theme_name, 'key': exception_key})
            self.__conjugator_verb_exceptions.append(updated_exception_data)
            self.__conjugator.set_irregular_verb_exceptions_config(self.__conjugator_verb_exceptions)
            Logger.log('L-0196')

    def update_fuzzy_gen_config(self, theme_name, theme_config_mod):
        """
        Actualiza un tema de configuración para el generador de terminos fuzzy. El thema solicitado debe existir
        y no puede ser el tema por defecto. Además el tema actualizado debe cumplir con la schema de validación.

        :theme_name: [String] - Nombre del tema a actualizar.

        :theme_config_mod: [Dict] - Objeto con los campos a actualizar del theme.
        """
        Logger.log('L-0171')
        existing_themes = self.__get_existing_themes(WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION)
        if not theme_name in existing_themes or theme_name == WORD_PROCESSOR_DEFAULT_THEME:
            ErrorHandler.raise_error('E-0052')
        current_theme_data = db_get_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION, {'theme': theme_name}, {'_id': 0, 'theme': 0})
        updated_theme_data = update_dict(current_theme_data, theme_config_mod)
        if not validate_config(WORD_PROCESSOR_SCHEMAS['FUZZY_GENERAL_CFG'], updated_theme_data):
            ErrorHandler.raise_error('E-0053')
        Logger.log('L-0174')
        Logger.log('L-0175')
        updated_theme_data['theme'] = theme_name
        updated_entries = db_update_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION, {'theme': theme_name}, updated_theme_data).matched_count
        if updated_entries <= 0:
            ErrorHandler.raise_error('E-0054')
        Logger.log('L-0176')
        if theme_name == self.__fuzzy_gen_active_theme:
            Logger.log('L-0177')
            self.__fuzzy_generator_cfg = updated_theme_data
            self.__fuzzy_generator.set_config(self.__fuzzy_generator_cfg)
            Logger.log('L-0178')

    def update_noun_conversor_config(self, theme_name, theme_config_mod):
        """
        Actualiza un tema de configuración para el conversor de sustantivos. El tema debe existir y no debe ser
        el tema por defecto. Además el tema debe cumplir con la schema de validación.

        :theme_name: [String] - Nombre del tema a actualizar.

        :theme_config_mod: [Dict] - Campos a modificar de la configuración actual.

        :return: [Bool] - True si la actualización es exitosa, False en caso contrario.
        """
        Logger.log('L-0180')
        existing_themes = self.__get_existing_themes(WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION)
        if not theme_name in existing_themes or theme_name == WORD_PROCESSOR_DEFAULT_THEME:
            ErrorHandler.raise_error('E-0055')
        current_theme_data = db_get_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION, {'theme': theme_name}, {'_id': 0, 'theme': 0})
        updated_theme_data = update_dict(current_theme_data, theme_config_mod)
        if not validate_config(WORD_PROCESSOR_SCHEMAS['NOUN_CONV_GENERAL_CFG'], updated_theme_data):
            ErrorHandler.raise_error('E-0056')
        Logger.log('L-0183')
        Logger.log('L-0184')
        updated_theme_data['theme'] = theme_name
        updated_entries = db_update_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION, {'theme': theme_name}, updated_theme_data).matched_count
        if updated_entries <= 0:
            ErrorHandler.raise_error('E-0057')
        Logger.log('L-0185')
        if theme_name == self.__noun_conversor_active_theme:
            Logger.log('L-0186')
            self.__noun_conversor_cfg = updated_theme_data
            self.__conversor.set_config(updated_theme_data)
            Logger.log('L-0187')

    def remove_conjugator_theme(self, theme_name):
        """
        Elimina completamente un tema de configuración para el conjugador. El tema debe existir, no se puede 
        eliminar el tema por defecto. Si el tema a a eliminar es el activo actualmente, se cambia el tema al tema por
        defecto.

        :theme_name: [String] - Nombre del tema.
        """
        Logger.log('L-0198')
        existing_themes = self.__get_existing_themes(WORD_PROCESSOR_CONJ_CFG_COLLECTION)
        if not theme_name in existing_themes or theme_name == WORD_PROCESSOR_DEFAULT_THEME:
            ErrorHandler.raise_error('E-0032')
        Logger.log('L-0200')
        if theme_name == self.__conjugator_active_theme:
            Logger.log('L-0201')
            self.set_conjugator_active_theme('default')
            Logger.log('L-0202')
        Logger.log('L-0204')
        db_batch_operation(WORD_PROCESSOR_CONFIG_DB, [
            {'type': DB_OPERATION_DELETE, 'col_name': WORD_PROCESSOR_CONJ_CFG_COLLECTION, 'query': {'theme': theme_name}},
            {'type': DB_OPERATION_DELETE_MANY, 'col_name': WORD_PROCESSOR_VERB_EXCEPTIONS_COLLECTION, 'query': {'theme': theme_name}},
            {'type': DB_OPERATION_DELETE, 'col_name': WORD_PROCESSOR_VERB_GROUPS_COLLECTION, 'query': {'theme': theme_name}}
        ])
        Logger.log('L-0205')

    def remove_fuzzy_gen_theme(self, theme_name):
        """
        Elimina completamente un tema de configuración para el generador fuzzy. El tema debe existir, no se puede
        eliminar el tema por defecto.

        :theme_name: [String] - Nombre del tema

        :return: [bool] - True si el borrado se realizó exitosamente, False en caso contrario.
        """
        Logger.log('L-0207')
        existing_themes = self.__get_existing_themes(WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION)
        if not theme_name in existing_themes or theme_name == WORD_PROCESSOR_DEFAULT_THEME:
            ErrorHandler.raise_error('E-0033')
        Logger.log('L-0209')
        if theme_name == self.__fuzzy_gen_active_theme:
            Logger.log('L-0210')
            self.set_fuzzy_generator_active_theme('default')
            Logger.log('L-0211')
        Logger.log('L-0213')
        db_delete_items(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION, {'theme': theme_name})
        Logger.log('L-0214')

    def remove_noun_conversor_theme(self, theme_name):
        """
        Elimina completamente un tema de configuración para el conversor de sustantivos. El tema debe existir, no se puede
        elimnar el tema por defecto.

        :theme_name: [String] - Nombre del tema
        """
        Logger.log('L-0216')
        existing_themes = self.__get_existing_themes(WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION)
        if not theme_name in existing_themes or theme_name == WORD_PROCESSOR_DEFAULT_THEME:
            ErrorHandler.raise_error('E-0034')
        Logger.log('L-0218')
        if theme_name == self.__noun_conversor_active_theme:
            Logger.log('L-0219')
            self.set_noun_conversor_active_theme('default')
            Logger.log('L-0220')
        Logger.log('L-0222')
        db_delete_items(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION, {'theme': theme_name})
        Logger.log('L-0223')

    def set_conjugator_active_theme(self, theme_name):
        """
        Cambia el tema de configuración activo del conjugador. En primera instancia guarda los cambios en la base de datos. El
        tema debe existir y no debe ser el tema actual.

        :theme_name: [String] - Nombre del tema
        """
        Logger.log('L-0141')
        if theme_name == self.__conjugator_active_theme:
            ErrorHandler.raise_error('E-0035')
        existing_themes = self.__get_existing_themes(WORD_PROCESSOR_CONJ_CFG_COLLECTION)
        if not theme_name in existing_themes:
            ErrorHandler.raise_error('E-0036')
        Logger.log('L-0144')
        Logger.log('L-0145')
        next_config_theme = db_get_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_CONJ_CFG_COLLECTION, {'theme': theme_name}, {'_id': 0})
        next_verb_exceptions = db_get_items(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_VERB_EXCEPTIONS_COLLECTION, {'theme': theme_name}, {'_id': 0})
        next_verb_groups = db_get_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_VERB_GROUPS_COLLECTION, {'theme': theme_name}, {'_id': 0})
        db_update_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_GENERAL_SETTING_COLLECTION, None, {'conjugator_active_theme': theme_name})
        self.__conjugator_active_theme = theme_name
        self.__conjugator_general_cfg = next_config_theme
        self.__conjugator_verb_exceptions = next_verb_exceptions
        self.__conjugator_verb_groups = next_verb_groups
        self.__conjugator.set_general_config(next_config_theme)
        self.__conjugator.set_irregular_verb_exceptions_config(next_verb_exceptions)
        self.__conjugator.set_irregular_verb_groups_config(next_verb_groups)
        Logger.log('L-0146')

    def set_fuzzy_generator_active_theme(self, theme_name):
        """
        Cambia el tema de configuración activo del generador fuzzy. En primera instancia guarda los cambios en la base de datos. El
        tema debe existir y no debe ser el tema actual.

        :theme_name: [String] - Nombre del tema
        """
        Logger.log('L-0148')
        if theme_name == self.__fuzzy_gen_active_theme:
            ErrorHandler.raise_error('E-0037')
        existing_themes = self.__get_existing_themes(WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION)
        if not theme_name in existing_themes:
            ErrorHandler.raise_error('E-0038')
        Logger.log('L-0151')
        Logger.log('L-0152')
        next_config_theme = db_get_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION, {'theme': theme_name}, {'_id': 0})
        db_update_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_GENERAL_SETTING_COLLECTION, None, {'fuzzy_gen_active_theme': theme_name})
        self.__fuzzy_gen_active_theme = theme_name
        self.__fuzzy_generator_cfg = next_config_theme
        self.__fuzzy_generator.set_config(next_config_theme)
        Logger.log('L-0153')

    def set_noun_conversor_active_theme(self, theme_name):
        """
        Cambia el tema de configuración activo del conversor de sustantivos. En primera instancia guarda los cambios en la base de
        datos. El tema debe existir y no debe ser el tema actual.

        :theme_name: [String] - Nombre del tema.

        :return: [Bool] - True si el cambio se realizó con exito. False en caso contrario.
        """
        Logger.log('L-0155')
        if theme_name == self.__noun_conversor_active_theme:
            ErrorHandler.raise_error('E-0039')
        existing_themes = self.__get_existing_themes(WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION)
        if not theme_name in existing_themes:
            ErrorHandler.raise_error('E-0040')
        Logger.log('L-0158')
        Logger.log('L-0159')
        next_config_theme = db_get_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION, {'theme': theme_name}, {'_id': 0})
        db_update_item(WORD_PROCESSOR_CONFIG_DB, WORD_PROCESSOR_GENERAL_SETTING_COLLECTION, None, {'fuzzy_gen_active_theme': theme_name})
        self.__noun_conversor_active_theme = theme_name
        self.__noun_conversor_cfg = next_config_theme
        self.__conversor.set_config(next_config_theme)
        Logger.log('L-0160')

    def conjugate_verb(self, verb=''):
        """
        Obtiene el objeto de conjugación para el verbo solicitado utilizando el conjugador. Si la inicialización no
        se hubiese realizado exitosamente no realiza la conjugación.

        :verb: [String] - verbo a conjugar.

        :return: [Dict] - Objeto de conjugación con las conjugaciones realizadas al verbo seleccionado. Si el objeto de
        configuración no esta correctamente inicializado devuelve None.
        """
        if not self.__init_success:
            return None
        return self.__conjugator.generar_conjugaciones(verb.lower())

    def conjugate_verb_table_view(self, verb=''):
        """
        Variación de conjugate_verb. Imprime por consola una tabla con la conjugación. Usar solo para testing. Si
        la inicialización no se ha realizado correctamente se sale prematuramente del método.

        :verb: [String] - Verbo a conjugar.
        """
        if not self.__init_success:
            return
        self.__conjugator.table_view(verb.lower())

    def get_fuzzy_set(self, term='', max_distance=1):
        """
        Obtiene un set de deformaciones para un termino que cumplan con la distancia máxima indicada. Si la inicialización
        no se ha realizado correctamente no se realiza la operación.

        :term: [String] - Termino a deformar.

        ;max_distanca: [Int] - Distancia de demerau-levenshtein máxima que puede tener el término deformado con el original,
        si no es provisto, por defecto será 1.

        :return: [Dict] - Si no se ha inicializado correctamente el controlador: None, En caso contrario devuelve un objeto
        con todas las deformaciones obtenidas.
        """
        if not self.__init_success:
            return None
        return self.__fuzzy_generator.get_fuzzy_tokens(term.lower(), max_distance)

    def get_plural(self, noun=''):
        """
        Obtiene el plural de un sustantivo. Si la inicialización no se ha completado correctamente no se realiza la operación.

        :noun: [String] - Sustantivo a partir del cual obtener el plural.

        :return: [String] - Si no se ha inicializado correctamente el controlado: None. En caso contrario, una cadena con el
        plural del sustantivo.
        """
        if not self.__init_success:
            return None
        return self.__conversor.a_plural(noun.lower())
