# @Error handler
from nlp_model_gen.packages.errorHandler.ErrorHandler import ErrorHandler

# @Classes
from nlp_model_gen.packages.applicationModule.ApplicationModuleController import ApplicationModuleController
from nlp_model_gen.packages.adminModule.AdminModuleController import AdminModuleController
from nlp_model_gen.packages.taskManager.TaskManager import TaskManager

# @Constants
from nlp_model_gen.constants.constants import (TASK_KEYS_MODEL_UPDATE, TASK_KEYS_WORD_PROCESSOR)

class SystemController:
    def __init__(self):
        self.__admin_module = None
        self.__application_module = None
        self.__task_manager = None
        self.__ready = False
        self.__init()

    def __init(self):
        """
        Inicializa el modulo
        """
        try:
            self.__admin_module = AdminModuleController()
            self.__application_module = ApplicationModuleController()
            self.__task_manager = TaskManager()
            self.__ready = True
        except:
            self.__ready = False

    def __build_response_object(self, operation_success, payload=None, error=None):
        """
        Construye el diccionario de respuesta para las solicitudes al controlador.

        :operation_success: [boolean] - Indica el exito de la tarea.

        :payload: [Dict] - Diccionario conteniendo los datos a retornar.
        """
        resource = payload
        if not operation_success:
            error_data = error
            if not error_data:
                error_data = ErrorHandler.get_error('E-0019', [])
            return {
                'success': False,
                'error_data': error_data
            }
        return {
            'success': operation_success,
            'resource': resource
        }
    
    def __process_incoming_request(self, action, task_check=None):
        """
        Procesa una solicitud entrante al sistema.

        :action: [Function] - Acción a realizar.

        :task_check: [List] - Validaciones a realizar en el administrador de tareas.
        """
        if not self.is_ready():
            return self.__build_response_object(False, error=ErrorHandler.get_error('E-0073', []))
        if task_check:
            if self.__task_manager.check_model_creation_tasks([TASK_KEYS_WORD_PROCESSOR]):
                return self.__build_response_object(False, error=ErrorHandler.get_error('E-0031', []))
        try:
            return action()
        except Exception as e:
            return self.__build_response_object(False, error=ErrorHandler.get_error_dict(e))

    def retry_init(self):
        """
        Reintenta la inicialización del módulo
        """
        self.__init()

    def is_ready(self):
        return self.__ready

    def generate_model(self, model_id, model_name, description, author, tokenizer_exceptions, max_dist):
        """
        Crea un nuevo modelo para el análisis de textos.

        :model_id: [String] - Id a asignar al nuevo modelo, el id se correspondera con el
        nombre que tendrá el directorio donde se guarde el modelo.

        :model_name: [String] - Nombre del modelo a crear.

        :description: [String] - Descripción del modelo.

        :author: [String] - Nombre del autor del modelo.

        :tokenizer_exceptions: [Dict] - Set de datos (semilla) que incluyen los datos
        necesarios para crear el modelo.

        :max_dist: [int] - Distancia de demerau levenstein máxima para las deformaciónes del
        modelo.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            task_id = self.__task_manager.create_model_creation_task(model_id, model_name, description, author, tokenizer_exceptions, max_dist)
            return self.__build_response_object(True, {'task_id': task_id})
        return self.__process_incoming_request(action)

    def delete_word_processor_theme(self, module_key, theme_name):
        """
        Elimina un tema para uno de los componentes del modulo de procesamiento de palabras.
        El tema debe existir y no puede haber ninguna tarea de creación de modelo pendiente o en
        ejecución al momento de realizar el borrado (solo si el tema indicado es el tema activo).

        :module_key: [String] - Clave del modulo sobre el cual se borrará el tema.

        :theme_name: [String] - Nombre del tema a borrar.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            self.__admin_module.delete_word_processor_theme(module_key, theme_name)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action, [TASK_KEYS_WORD_PROCESSOR])

    def update_theme_conjugator_exceptions(self, theme_name, exception_key, exception_data):
        """
        Actualiza una excepción para un tema particular del conjugador. La excepción y el tema
        deben existir. Además, no podrá haber una tarea de creación de modelo pendiente o en 
        ejecución (solo si el tema indicado es el tema activo).

        :theme_name: [String] - Nombre del tema del conjugador a modificar.

        :exception_key: [String] - Clave de la excepción a actualizar.

        :exception_data: [Dict] - Diccionario con la nueva configuración de la excepción.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            self.__admin_module.update_theme_conjugator_exceptions(theme_name, exception_key, exception_data)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action, [TASK_KEYS_WORD_PROCESSOR])

    def update_word_processor_config_theme(self, module_key, theme_name, config_mod, irregular_groups_mod=None):
        """
        Actualiza / edita un tema de configuración para un componente particular del conjugador. La
        tanto el modulo como el tema deben existir. Además, no puede existir una tarea de creación de
        modelo pendiente o en ejecución al momento de ejecutar esta tarea (solo si el tema indicado es 
        el tema activo)

        :module_key: [String] - Clave del modulo a actualizar.

        :theme_name: [String] - Nombre del tema a actualizar.

        :config_mod: [Dict] - Campos a actualizar, solo son necesarios los campos a modificar.

        :irregular_groups_mod: [Dict] - Campos a actualizar de los grupos irregulares, solo son necesarios
        los campos a actualizar. Solo es requerido cuando se actualiza el modulo de conjugación.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            self.__admin_module.update_word_processor_config_theme(module_key, theme_name, config_mod, irregular_groups_mod)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action, [TASK_KEYS_WORD_PROCESSOR])

    def set_word_processor_active_theme(self, module_key, theme_name):
        """
        Cambia el tema activo para el modulo de procesamiento de palabras, tanto el modulo como el
        tema deben existir. No se podrá realizar esta operación si hay una tarea de creación de modelo
        pendiente o en ejecución.

        :module_key: [String] - Clave del modulo a actualizar.

        :theme_name: [String] - Nombre del tema a utilizar.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            self.__admin_module.set_word_processor_active_theme(module_key, theme_name)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action, [TASK_KEYS_WORD_PROCESSOR])

    def get_word_processor_active_themes(self): 
        """
        Devuelve un objeto con los temas activos para cada modulo del conjugador de palabras

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            active_themes = self.__admin_module.get_word_processor_active_themes()
            return self.__build_response_object(True, {'active_themes': active_themes})
        return self.__process_incoming_request(action)

    def add_theme_conjugator_exceptions(self, theme_name, exceptions):
        """
        Agrega un set de excepciones a un tema del conjugador. El tema debe existir y, si fuera
        el tema activo en el momento de realizar la operación, no puede haber una operación de 
        creación de modelo pendiente o activa. Además no deben haber excepciones ya registradas
        para las nuevas excepciones a agregar.

        :theme_name: [String] - Nombre del tema.

        :exceptions: [List(Dict)] - Lista de excepciones a agregar para el tema de configuración.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            self.__admin_module.add_theme_conjugator_exceptions(theme_name, exceptions)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action, [TASK_KEYS_WORD_PROCESSOR])

    def add_word_processor_config_theme(self, module_key, theme_name, configs, irregular_groups=None):
        """
        Agrega un nuevo tema de configuración para alguno de los submodulos del modulo de 
        procesamiento de palabras. El submodulo debe existir y no debe existir un tema con
        el nombre solicitado ya registrado.

        :module_key: [String] - Clave del submodulo.

        :theme_name: [String] - Nombre del nuevo tema.

        :configs: [Dict] - Configuración del nuevo tema, debe cumplir con la validación de
        schema para el submodulo particular.

        :irregular_groups: [Dict] - Configuración de los grupos irregulares. Solo es necesario
        para los nuevos temas del modulo de conjugación.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            self.__admin_module.add_word_processor_config_theme(module_key, theme_name, configs, irregular_groups)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action, [TASK_KEYS_WORD_PROCESSOR])

    def get_word_processor_available_configs(self, module_key):
        """
        Devuelve un listado con los temas de configuración disponibles para el submodulo
        solicitado del modulo de procesamiento de palabras.

        :module_key: [String] - Clave del submodulo.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            available_configs = self.__admin_module.get_word_processor_available_configs(module_key)
            return self.__build_response_object(True, {'available_configs': available_configs})
        return self.__process_incoming_request(action)

    def delete_model(self, model_id):
        """
        Elimina un modelo. El modelo debe existir, además esta operación no podrá realizarse si
        hay alguna tarea de entrenamiento o análisis de texto pendiente para el modelo.

        :model_id: [String] - Id del modelo.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            self.__admin_module.delete_model_data(model_id)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action, [TASK_KEYS_MODEL_UPDATE])

    def edit_model_data(self, model_id, new_model_name=None, new_description=None):
        """
        Edita los datos del modelo identificado con el id solicitado. El modelo debe existir.
        No hay restricciones para la realización de esta operación.

        :model_id: [String] - Id del modelo a editar.

        :new_model_name: [String] - Nuevo nombre a aplicar al modelo (si no es provisto se
        mantendrá el actual).

        :new_description: [String] - Nueva descripción a aplicar al modelo (si no es provista
        se mantendrá la actual).

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            self.__admin_module.edit_model_data(model_id, new_model_name, new_description)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action)

    def get_available_models(self):
        """
        Devuelve un listado con los modelos disponibles y sus datos.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            available_models = self.__admin_module.get_available_models()
            return self.__build_response_object(True, available_models)
        return self.__process_incoming_request(action)

    def approve_training_examples(self, training_examples_list):
        """
        Aprueba un conjunto de ejemplos de entrenamiento. Los ejemplos deben existir.

        :training_examples_list: [List(int)] - Lista de los ids de los ejemplos a aprobar.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            results = self.__admin_module.approve_training_examples(training_examples_list)
            return self.__build_response_object(True, {'results': results})
        return self.__process_incoming_request(action)
    
    def discard_training_examples(self, training_examples_list):
        """
        Rechaza un conjunto de ejemplos de entrenamiento. Los ejemplos deben existir.

        :training_examples_list: [List(int)] - Lista de los ids de los ejemplos a aprobar.

        :return: [Dict] - Resultados de la tarea
        """
        def action():
            results = self.__admin_module.discard_training_examples(training_examples_list)
            return self.__build_response_object(True, {'results': results})
        return self.__process_incoming_request(action)

    def get_submitted_training_examples(self, model_id, status):
        """
        Obtiene un listado de los ejemplos de entrenamiento existentes para un determinado modelo.

        :model_id: [String] - Id del modelo para el cual obtener los ejemplos.

        :status: [String] - Estado de los ejemplos a buscar.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            submitted_training_examples = self.__admin_module.get_submitted_training_examples(model_id, status)
            return self.__build_response_object(True, {'status': status, 'examples': submitted_training_examples})
        return self.__process_incoming_request(action)

    def submit_training_examples(self, model_id, examples):
        """
        Registra un set de ejemplos de entrenamiento para un modelo particular. El modelo debe existir
        y los ejemplos deben validar con la schema de validación para los ejemplos.

        :model_id: [String] - Id del modelo.

        :examples: [List(Dict)] - Listado de ejemplos. Debe haber al menos un ejemplo.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            self.__admin_module.submit_training_examples(model_id, examples)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action)

    def submit_single_training_example(self, model_id, example):
        """
        Registra un único ejemplo de entrenamiento utilizando el módulo de aplicación para ello.

        :model_id: [String] - Id del modelo.

        :example: [Dict] - Ejemplo de entrenamiento a agregar.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            self.__application_module.submit_training_example(model_id, example)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action)

    def apply_approved_training_examples(self, model_id):
        """
        Inicia un proceso de entrenamiento para un modelo. Aplicando todos los ejemplos de entrenamiento
        aprobados que haya en el sistema.

        :model_id: [String] - Id del modelo.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            task_id = self.__task_manager.create_model_training_task(model_id)
            return self.__build_response_object(True, {'task_id': task_id})
        return self.__process_incoming_request(action, [TASK_KEYS_MODEL_UPDATE])

    def analyze_text(self, model_id, text, only_positives=False):
        """
        Analiza un texto utilizando el modelo deseado. El modelo debe existir. Si no se activa el flag
        de solo positivos, se devolverán todos los resultados independientemente de aquellos que se 
        hayan detectado como positivos.

        :model_id: [String] - Id del modelo.

        :text: [String] - Texto a analizar.

        :only_positives: [boolean] - Flag que indica si solo devolver los resultados positivos del 
        análisis con el modelo. Por defecto sera falsa.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            task_id = self.__task_manager.create_text_analysis_task(model_id, text, only_positives)
            return self.__build_response_object(True, {'task_id': task_id})
        return self.__process_incoming_request(action)

    def get_task_status(self, task_id):
        """
        Devuelve el estado de una tarea particular. La tarea debe existir.

        :task_id: [int] - Id de la tarea.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            task_status = self.__task_manager.get_task_status(task_id)
            return self.__build_response_object(True, task_status)
        return self.__process_incoming_request(action)

    def get_available_tagging_entities(self):
        """
        Devuelve un listado con las entitades de etiquetado para el NER disponibles en el sistema.

        :return: [Dict] - Resultados de la tarea.
        """
        def action():
            tagging_entities = self.__application_module.get_available_tagging_entities()
            return self.__build_response_object(True, {'custom_entities': tagging_entities})
        return self.__process_incoming_request(action)

    def analyze_files(self, model_id, files, only_positives):
        """
        Analiza un conjunto de archivos (ya abiertos) de manera similar a como analizaría un
        único texto.

        :model_id: [String] - Id del modelo a utilizar para el analisis.

        :files: [List(File)] - Lista de archivos a analizar.

        :only_positives: [boolean] - Indica si solo deben informarse los resultados positivos.

        :return: [Dict] - Diccionario con los resultados de la operación.
        """
        def action():
            task_id = self.__task_manager.create_files_analysis_task(model_id, files, only_positives)
            return self.__build_response_object(True, {'task_id': task_id})
        return self.__process_incoming_request(action)

    def add_custom_entity(self, name, description):
        """
        Agrega una nueva entidad personalizada al administrador de ejemplos de entrenamiento.

        :name: [String] - Nombre de la entidad.

        :description: [String] - Descripción de la entidad personalizada.

        :return: [Dict] - Diccionario con los resultados de la operación
        """
        def action():
            self.__admin_module.add_custom_entity(name, description)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action)

    def edit_custom_entity(self, name, description):
        """
        Edita una entidad personalizada del administrador de ejemplos de entrenamiento.

        :name: [String] - Nombre de la entidad a editar.

        :description: [String] - Nueva descripción para la entidad personalizada.

        :return: [Dict] - Diccionario con los resultados de la operación
        """
        def action():
            self.__admin_module.edit_custom_entity(name, description)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action)

    def add_analyzer_exception(self, model_id, base_form, token_text, enabled=True):
        """
        Agrega una excepción al analizador para un modelo particular.

        :model_id: [String] - Id del modelo.

        :base_form: [String] - Forma base del token.

        :token_text: [String] - Forma especifica en la que detectar el token.

        :enabled: [boolean] - True si esta habilitada, False en caso contrario (por defecto
        True)

        :return: [Dict] - Diccionario con los resultados de la operación
        """
        def action():
            self.__admin_module.add_analyzer_exception(model_id, base_form, token_text, enabled)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action, [TASK_KEYS_MODEL_UPDATE])

    def enable_analyzer_exception(self, model_id, base_form, token_text):
        """
        Habilita una excepción del analizador. La misma no debe estar habilitada
        previamente.

        :model_id: [String] - Id del modelo.

        :base_form: [String] - Forma base del token.

        :token_text: [String] - Forma especifica en la que detectar el token.

        :return: [Dict] - Diccionario con los resultados de la operación
        """
        def action():
            self.__admin_module.enable_analyzer_exception(model_id, base_form, token_text)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action, [TASK_KEYS_MODEL_UPDATE])

    def disable_analyzer_exception(self, model_id, base_form, token_text):
        """
        Deshabilita una excepción del analizador. La misma no debe estar habilitada
        previamente.

        :model_id: [String] - Id del modelo.

        :base_form: [String] - Forma base del token.

        :token_text: [String] - Forma especifica en la que detectar el token.

        :return: [Dict] - Diccionario con los resultados de la operación
        """
        def action():
            self.__admin_module.disable_analyzer_exception(model_id, base_form, token_text)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action, [TASK_KEYS_MODEL_UPDATE])

    def get_analyzer_exceptions(self, model_id):
        """
        Obtiene un listado de todas las excepciones al analizador para un modelo
        particular.

        :model_id: [String] - Id del modelo.

        :return: [Dict] - Diccionario con los resultados de la operación
        """
        def action():
            results = self.__admin_module.get_analyzer_exceptions(model_id)
            return self.__build_response_object(True, results)
        return self.__process_incoming_request(action)

    def import_model(self, model_id, source=None):
        """
        Importa un modelo existente desde el repositorio de modelos. No debe existir
        un modelo local con dicho id y, además, el módelo debe existir en el repositorio
        remoto de modelos.

        :model_id: [String] - Id del modelo a importar.

        :source: [Dict] - Fuente de donde obtener el modelo, puede ser un repositorio
        git o un directorio local.
        """
        def action():
            self.__admin_module.import_model(model_id, source)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action, [TASK_KEYS_MODEL_UPDATE])

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
        def action():
            self.__admin_module.export_model(model_id, output_path, split)
            return self.__build_response_object(True)
        return self.__process_incoming_request(action, [TASK_KEYS_MODEL_UPDATE])
