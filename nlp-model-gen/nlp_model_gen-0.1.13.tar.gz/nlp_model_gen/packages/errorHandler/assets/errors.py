GENERIC_ERROR = {
    'error_code': 'E-0001', 
    'description': 'Error generico', 
    'source': {'class': 'N/A', 'method': 'N/A'},
    'log': None
}
UNKNOWN_ERROR = {
    'error_code': 'E-0109', 
    'description': 'Error desconocido', 
    'source': {'class': 'N/A', 'method': 'N/A'},
    'log': None
}
ERROR_DATA = {
    'E-0002': {
        'description': 'Error al obtener colección de datos en la base de datos',
        'source': {'class': '', 'method': 'db_check_collection'},
        'log': 'L-0085'
    },
    'E-0003': {
        'description': 'Error al obtener elementos de la base de datos',
        'source': {'class': '', 'method': 'db_get_item'},
        'log': 'L-0086'
    },
    'E-0004': {
        'description': 'Error al obtener elementos de la base de datos',
        'source': {'class': '', 'method': 'db_get_items'},
        'log': 'L-0087'
    },
    'E-0005': {
        'description': 'Error al insertar elementos en la base de datos',
        'source': {'class': '', 'method': 'db_insert_item'},
        'log': 'L-0088'
    },
    'E-0006': {
        'description': 'Error al insertar elementos en la base de datos',
        'source': {'class': '', 'method': 'db_insert_items'},
        'log': 'L-0089'
    },
    'E-0007': {
        'description': 'Error al actualizar elementos en la base de datos',
        'source': {'class': '', 'method': 'db_update_item'},
        'log': None
    },
    'E-0008': {
        'description': 'Error al actualizar elementos en la base de datos',
        'source': {'class': '', 'method': 'db_update_many'},
        'log': None
    },
    'E-0009': {
        'description': 'Error al eliminar elemento de la base de datos',
        'source': {'class': '', 'method': 'db_delete_item'},
        'log': 'L-0090'
    },
    'E-0010': {
        'description': 'Error al eliminar elementos de la base de datos',
        'source': {'class': '', 'method': 'db_delete_items'},
        'log': 'L-0091'
    },
    'E-0011': {
        'description': 'Error al eliminar colección de la base de datos',
        'source': {'class': '', 'method': 'db_drop_collection'},
        'log': 'L-0092'
    },
    'E-0012': {
        'description': 'Error al procesar operación en batch',
        'source': {'class': '', 'method': 'db_batch_operation'},
        'log': 'L-0093'
    },
    'E-0013': {
        'description': 'Error al leer archivo JSON',
        'source': {'class': '', 'method': 'load_json_file'},
        'log': 'L-0357'
    },
    'E-0014': {
        'description': 'Error al escribir archivo JSON',
        'source': {'class': '', 'method': 'overwrite_json_file'},
        'log': 'L-0358'
    },
    'E-0015': {
        'description': 'Error al escribir archivo JSON',
        'source': {'class': '', 'method': 'remove_dir'},
        'log': 'L-0083'
    },
    'E-0016': {
        'description': 'Error al escribir archivo',
        'source': {'class': '', 'method': 'dictionary_to_disk'},
        'log': 'L-0359'
    },
    'E-0017': {
        'description': 'Error al obtener archivos',
        'source': {'class': '', 'method': 'get_files_in_dir'},
        'log': 'L-0360'
    },
    'E-0018': {
        'description': 'Error al copiar archivos',
        'source': {'class': '', 'method': 'copy_file'},
        'log': 'L-0361'
    },
    'E-0019': {
        'description': 'Error generico en el controlador de sistema',
        'source': {'class': 'SystemController', 'method': 'build_response_object'},
        'log': None
    },
    'E-0020': {
        'description': 'Error al inicializar modulo de procesamiento de palabras',
        'source': {'class': 'WordProcessorController', 'method': 'initializate_cfg'},
        'log': 'L-0040'
    },
    'E-0021': {
        'description': 'Error al inicializar modulo de gestión de modelos',
        'source': {'class': 'ModelManagerController', 'method': 'initialize'},
        'log': 'L-0053'
    },
    'E-0022': {
        'description': 'Error al inicializar modulo de gestión de modelos desde modulo de entrenamiento',
        'source': {'class': 'ModelTrainingController', 'method': 'init'},
        'log': 'L-0244'
    },
    'E-0023': {
        'description': 'Error al incializar modulo de datos de entrenamiento',
        'source': {'class': 'TrainDataManager', 'method': 'init'},
        'log': 'L-0256'
    },
    'E-0024': {
        'description': 'Error al inicializar el modulo de etiquetas personalizadas',
        'source': {'class': 'CustomEntityTagManager', 'method': 'init'},
        'log': 'L-0263'
    },
    'E-0025': {
        'description': 'Ya existe un modelo con el id deseado',
        'source': {'class': 'AdminModuleController', 'method': 'generate_model'},
        'log': None
    },
    'E-0026': {
        'description': 'La semilla de excepciones del tokenizer no es valida',
        'source': {'class': 'AdminModuleController', 'method': 'generate_model'},
        'log': None
    },
    'E-0027': {
        'description': 'El directorio temporal requerido para el modelo se encuentra ocupado',
        'source': {'class': 'TokenizerRulesGenerator', 'method': 'generate_model_data'},
        'log': None
    },
    'E-0028': {
        'description': 'Error al cargar modelo base de Spacy',
        'source': {'class': 'ModelLoader', 'method': 'initiate_default_model'},
        'log': None
    },
    'E-0029': {
        'description': 'El modelo ya existe en la base de datos',
        'source': {'class': 'ModelDataManager', 'method': 'save_model_data'},
        'log': 'L-0027'
    },
    'E-0030': {
        'description': 'El directorio donde debe guardarse el modelo ya existe',
        'source': {'class': 'ModelLoader', 'method': 'save_model'},
        'log': 'L-0031'
    },
    'E-0031': {
        'description': 'La acción se bloqueo por que existe una tarea relacionada pendiente',
        'source': {'class': 'SystemController', 'method': 'process_incoming_request'},
        'log': None
    },
    'E-0032': {
        'description': 'El tema seleccionado no existe o es el tema por defecto',
        'source': {'class': 'WordProcessorController', 'method': 'remove_conjugator_theme'},
        'log': 'L-0199'
    },
    'E-0033': {
        'description': 'El tema seleccionado no existe o es el tema por defecto',
        'source': {'class': 'WordProcessorController', 'method': 'remove_fuzzy_gen_theme'},
        'log': 'L-0208'
    },
    'E-0034': {
        'description': 'El tema seleccionado no existe o es el tema por defecto',
        'source': {'class': 'WordProcessorController', 'method': 'remove_noun_conversor_theme'},
        'log': 'L-0217'
    },
    'E-0035': {
        'description': 'El tema seleccionado ya es el tema activo',
        'source': {'class': 'WordProcessorController', 'method': 'set_conjugator_active_theme'},
        'log': 'L-0142'
    },
    'E-0036': {
        'description': 'El tema seleccionado no existe',
        'source': {'class': 'WordProcessorController', 'method': 'set_conjugator_active_theme'},
        'log': 'L-0143'
    },
    'E-0037': {
        'description': 'El tema seleccionado ya es el tema activo',
        'source': {'class': 'WordProcessorController', 'method': 'set_fuzzy_generator_active_theme'},
        'log': 'L-0149'
    },
    'E-0038': {
        'description': 'El tema seleccionado no existe',
        'source': {'class': 'WordProcessorController', 'method': 'set_fuzzy_generator_active_theme'},
        'log': 'L-0150'
    },
    'E-0039': {
        'description': 'El tema seleccionado ya es el tema activo',
        'source': {'class': 'WordProcessorController', 'method': 'set_noun_conversor_active_theme'},
        'log': 'L-0156'
    },
    'E-0040': {
        'description': 'El tema seleccionado no existe',
        'source': {'class': 'WordProcessorController', 'method': 'set_noun_conversor_active_theme'},
        'log': 'L-0157'
    },
    'E-0041': {
        'description': 'Hay una tarea de creación de modelos en curso',
        'source': {'class': 'SystemController', 'method': 'update_word_processor_config_theme'},
        'log': None
    },
    'E-0042': {
        'description': 'El modulo del procesador de palabras especificado no existe',
        'source': {'class': 'AdminModuleController', 'method': 'set_word_processor_active_theme'},
        'log': None
    },
    'E-0043': {
        'description': 'El modulo del procesador de palabras especificado no existe',
        'source': {'class': 'AdminModuleController', 'method': 'delete_word_processor_theme'},
        'log': None
    },
    'E-0044': {
        'description': 'Hay una tarea de creación de modelos en curso',
        'source': {'class': 'SystemController', 'method': 'update_theme_conjugator_exceptions'},
        'log': None
    },
    'E-0045': {
        'description': 'Hay una tarea de creación de modelos en curso',
        'source': {'class': 'SystemController', 'method': 'update_word_processor_config_theme'},
        'log': None
    },
    'E-0046': {
        'description': 'La excepción no existe o se esta intentando modificar el tema por defecto',
        'source': {'class': 'WordProcessorController', 'method': 'update_conjugator_exception'},
        'log': 'L-0190'
    },
    'E-0047': {
        'description': 'La configuración de la excepción no tiene la estructura correcta',
        'source': {'class': 'WordProcessorController', 'method': 'update_conjugator_exception'},
        'log': 'L-0191'
    },
    'E-0048': {
        'description': 'No se ha podido actualizar la excepción en la base de datos',
        'source': {'class': 'WordProcessorController', 'method': 'update_conjugator_exception'},
        'log': None
    },
    'E-0049': {
        'description': 'El modulo del procesador de palabras especificado no existe',
        'source': {'class': 'AdminModuleController', 'method': 'update_word_processor_config_theme'},
        'log': None
    },
    'E-0050': {
        'description': 'El tema a actualizar no existe o es el tema por defecto',
        'source': {'class': 'WordProcessorController', 'method': 'update_conjugator_configs'},
        'log': 'L-0163'
    },
    'E-0051': {
        'description': 'Las configuraciones provistas no tienen la estructura correcta',
        'source': {'class': 'WordProcessorController', 'method': 'update_conjugator_configs'},
        'log': 'L-0164'
    },
    'E-0052': {
        'description': 'El tema a actualizar no existe o es el tema por defecto',
        'source': {'class': 'WordProcessorController', 'method': 'update_fuzzy_gen_config'},
        'log': 'L-0172'
    },
    'E-0053': {
        'description': 'La configuración provista no tiene la estructura correcta',
        'source': {'class': 'WordProcessorController', 'method': 'update_fuzzy_gen_config'},
        'log': 'L-0173'
    },
    'E-0054': {
        'description': 'No se ha podido actualizar la configuración en la base de datos',
        'source': {'class': 'WordProcessorController', 'method': 'update_fuzzy_gen_config'},
        'log': None
    },
    'E-0055': {
        'description': 'El tema a actualizar no existe o es el tema por defecto',
        'source': {'class': 'WordProcessorController', 'method': 'update_noun_conversor_config'},
        'log': 'L-0181'
    },
    'E-0056': {
        'description': 'La configuración provista no tiene la estructura correcta',
        'source': {'class': 'WordProcessorController', 'method': 'update_noun_conversor_config'},
        'log': 'L-0182'
    },
    'E-0057': {
        'description': 'No se ha podido actualizar la configuración en la base de datos',
        'source': {'class': 'WordProcessorController', 'method': 'update_noun_conversor_config'},
        'log': None
    },
    'E-0058': {
        'description': 'Hay una tarea de creación de modelos en curso',
        'source': {'class': 'SystemController', 'method': 'add_theme_conjugator_exceptions'},
        'log': None
    },
    'E-0059': {
        'description': 'El tema seleccionado no existe o es el tema por defecto',
        'source': {'class': 'WordProcessorController', 'method': 'add_conjugator_exceptions'},
        'log': 'L-0118'
    },
    'E-0060': {
        'description': 'La configuración de la excepción no tiene la estructura correcta',
        'source': {'class': 'WordProcessorController', 'method': 'add_conjugator_exceptions'},
        'log': 'L-0121'
    },
    'E-0061': {
        'description': 'Ya existe una excepción con la clave seleccionada',
        'source': {'class': 'WordProcessorController', 'method': 'add_conjugator_exceptions'},
        'log': 'L-0122'
    },
    'E-0062': {
        'description': 'Hay una tarea de creación de modelos en curso',
        'source': {'class': 'SystemController', 'method': 'add_word_processor_config_theme'},
        'log': None
    },
    'E-0063': {
        'description': 'El modulo del procesador de palabras especificado no existe',
        'source': {'class': 'AdminModuleController', 'method': 'add_word_processor_config_theme'},
        'log': None
    },
    'E-0064': {
        'description': 'El tema solicitado ya existe',
        'source': {'class': 'WordProcessorController', 'method': 'add_conjugator_config'},
        'log': None
    },
    'E-0065': {
        'description': 'Alguna de las configuraciones no posee la estructura correcta',
        'source': {'class': 'WordProcessorController', 'method': 'add_conjugator_config'},
        'log': 'L-0112'
    },
    'E-0066': {
        'description': 'El tema solicitado ya existe',
        'source': {'class': 'WordProcessorController', 'method': 'add_fuzzy_gen_config'},
        'log': None
    },
    'E-0067': {
        'description': 'Alguna de las configuraciones no posee la estructura correcta',
        'source': {'class': 'WordProcessorController', 'method': 'add_fuzzy_gen_config'},
        'log': 'L-0130'
    },
    'E-0068': {
        'description': 'El tema solicitado ya existe',
        'source': {'class': 'WordProcessorController', 'method': 'add_noun_conversor_config'},
        'log': None
    },
    'E-0069': {
        'description': 'Alguna de las configuraciones no posee la estructura correcta',
        'source': {'class': 'WordProcessorController', 'method': 'add_noun_conversor_config'},
        'log': 'L-0136'
    },
    'E-0070': {
        'description': 'Hay una tarea de análisis o de actualización en curso',
        'source': {'class': 'SystemController', 'method': 'delete_model'},
        'log': None
    },
    'E-0071': {
        'description': 'El modelo seleccionado no existe',
        'source': {'class': 'ModelManagerController', 'method': 'remove_model'},
        'log': 'L-0065'
    },
    'E-0072': {
        'description': 'No se ha podido eliminar el modelo de la base de datos',
        'source': {'class': 'ModelDataManager', 'method': 'remove_model_data'},
        'log': 'L-0068'
    },
    'E-0073': {
        'description': 'El controlador del sistema no se ha inicializado correctamente',
        'source': {'class': 'SystemController', 'method': 'process_incoming_request'},
        'log': None
    },
    'E-0074': {
        'description': 'El modelo solicitado no existe',
        'source': {'class': 'AdminModuleController', 'method': 'edit_model_data'},
        'log': 'L-0075'
    },
    'E-0075': {
        'description': 'Los datos a actualizar son los mismos que los actuales',
        'source': {'class': 'AdminModuleController', 'method': 'edit_model_data'},
        'log': 'L-0076'
    },
    'E-0076': {
        'description': 'Los datos del modelo no han podido ser actualizados en la base de datos',
        'source': {'class': 'ModelDataManager', 'method': 'modify_model_data'},
        'log': None
    },
    'E-0077': {
        'description': 'No existe ningún ejemplo para el Id indicado',
        'source': {'class': 'TrainDataManager', 'method': 'approve_example'},
        'log': 'L-0308'
    },
    'E-0078': {
        'description': 'El ejemplo indicado no se encuentra en estado <submitted>',
        'source': {'class': 'TrainDataManager', 'method': 'approve_example'},
        'log': 'L-0354'
    },
    'E-0079': {
        'description': 'No se han podido actualizar los datos del ejemplo en la base de datos',
        'source': {'class': 'TrainDataManager', 'method': 'approve_example'},
        'log': 'L-0312'
    },
    'E-0080': {
        'description': 'El estado solicitado no existe o no es válido para la solicitud',
        'source': {'class': 'AdminModuleController', 'method': 'get_submitted_training_examples'},
        'log': None
    },
    'E-0081': {
        'description': 'El modelo solicitado no existe',
        'source': {'class': 'TrainDataManager', 'method': 'get_approved_examples'},
        'log': None
    },
    'E-0082': {
        'description': 'El modelo solicitado no existe',
        'source': {'class': 'TrainDataManager', 'method': 'get_approved_examples'},
        'log': 'L-0325'
    },
    'E-0083': {
        'description': 'El modelo solicitado no existe',
        'source': {'class': 'TrainDataManager', 'method': 'get_approved_examples'},
        'log': None
    },
    'E-0084': {
        'description': 'El modelo solicitado no existe',
        'source': {'class': 'ModelTrainingController', 'method': 'add_training_examples'},
        'log': 'L-0294'
    },
    'E-0085': {
        'description': 'No se ha encontrado el administrador de datos de entrenamiento para el modelo',
        'source': {'class': 'TrainDataManager', 'method': 'add_training_examples'},
        'log': 'L-0298'
    },
    'E-0086': {
        'description': 'La estructura de alguno de los ejemplos no es válida',
        'source': {'class': 'TrainDataManager', 'method': 'create_new_example_data'},
        'log': None
    },
    'E-0087': {
        'description': 'Alguna de las etiquetas personalizadas no existe',
        'source': {'class': 'TrainDataManager', 'method': 'validate_examples'},
        'log': None
    },
    'E-0088': {
        'description': 'El modelo seleccionado no existe',
        'source': {'class': 'ModelTrainingController', 'method': 'apply_training_approved_examples'},
        'log': 'L-0332'
    },
    'E-0089': {
        'description': 'El modelo seleccionado no cuenta con ejemplos de entrenamiento aprobados',
        'source': {'class': 'ModelTrainingController', 'method': 'apply_training_approved_examples'},
        'log': 'L-0333'
    },
    'E-0090': {
        'description': 'No se pudo encontrar el set de ejemplos del modelo',
        'source': {'class': 'ModelTrainerManager', 'method': 'train_model'},
        'log': 'L-0337'
    },
    'E-0091': {
        'description': 'No se han encontrado datos de entrenamiento',
        'source': {'class': 'Model', 'method': 'train_model'},
        'log': None
    },
    'E-0092': {
        'description': 'Error al cargar el modelo de Spacy',
        'source': {'class': 'ModelLoader', 'method': 'load_model'},
        'log': 'L-0341'
    },
    'E-0093': {
        'description': 'Error al actualizar el estado de los ejemplos en la base de datos',
        'source': {'class': 'TrainDataManager', 'method': 'set_applied_state'},
        'log': None
    },
    'E-0094': {
        'description': 'El texto a analizar no es valido',
        'source': {'class': 'DataSanitizer', 'method': 'sanitize_text_for_analysis'},
        'log': None
    },
    'E-0095': {
        'description': 'El modelo solicitado no existe',
        'source': {'class': 'ModelManagerController', 'method': 'analyze_text'},
        'log': 'L-0055'
    },
    'E-0096': {
        'description': 'El archivo provisto no tiene el formato correcto',
        'source': {'class': 'FilesAnalysisTask', 'method': 'task_init_hook'},
        'log': None
    },
    'E-0097': {
        'description': 'La tarea solicitada no existe',
        'source': {'class': 'TaskManager', 'method': 'get_task_status'},
        'log': None
    },
    'E-0098': {
        'description': 'La entidad personalizada no cumple con la estructura requerida',
        'source': {'class': 'ModelTrainingController', 'method': 'add_custom_entity'},
        'log': 'L-0267'
    },
    'E-0099': {
        'description': 'Ya existe una entidad con el nombre solicitado',
        'source': {'class': 'CustomEntityTagManager', 'method': 'add_custom_entity'},
        'log': 'L-0272'
    },
    'E-0100': {
        'description': 'La entidad personalizada no cumple con la estructura requerida',
        'source': {'class': 'ModelTrainingController', 'method': 'edit_custom_entity'},
        'log': 'L-0280'
    },
    'E-0101': {
        'description': 'La entidad personalizada a editar no existe',
        'source': {'class': 'CustomEntityTagManager', 'method': 'edit_custom_tag_entity'},
        'log': 'L-0285'
    },
    'E-0102': {
        'description': 'Los datos a modificar son iguales a los existentes',
        'source': {'class': 'CustomEntityTagManager', 'method': 'edit_custom_tag_entity'},
        'log': 'L-0286'
    },
    'E-0103': {
        'description': 'Los datos no se han actualizado en la base de datos',
        'source': {'class': 'CustomEntityTagManager', 'method': 'edit_custom_tag_entity'},
        'log': 'L-0289'
    },
    'E-0104': {
        'description': 'No existe ningún ejemplo para el Id indicado',
        'source': {'class': 'TrainDataManager', 'method': 'discard_example'},
        'log': 'L-0317'
    },
    'E-0105': {
        'description': 'El ejemplo indicado no se encuentra en estado <submitted>',
        'source': {'class': 'TrainDataManager', 'method': 'discard_example'},
        'log': 'L-0355'
    },
    'E-0106': {
        'description': 'No se han podido actualizar los datos del ejemplo en la base de datos',
        'source': {'class': 'TrainDataManager', 'method': 'discard_example'},
        'log': 'L-0321'
    },
    'E-0107': {
        'description': 'El modelo solicitado no existe',
        'source': {'class': 'ModelManagerController', 'method': 'add_analyzer_exception'},
        'log': 'L-0005'
    },
    'E-0108': {
        'description': 'La excepción ya esta registrada para el modelo solicitado',
        'source': {'class': 'ModelManagerController', 'method': 'add_analyzer_exception'},
        'log': 'L-0012'
    },
    'E-0110': {
        'description': 'El modelo solicitado no existe',
        'source': {'class': 'ModelManagerController', 'method': 'get_analyzer_exceptions'},
        'log': 'L-0097'
    },
    'E-0111': {
        'description': 'El modelo solicitado no existe',
        'source': {'class': 'ModelManagerController', 'method': 'enable_analyzer_exception'},
        'log': 'L-0028'
    },
    'E-0112': {
        'description': 'La excepción no existe o ya se encuentra habilitada',
        'source': {'class': 'ModelManagerController', 'method': 'enable_analyzer_exception'},
        'log': 'L-0033'
    },
    'E-0113': {
        'description': 'No se han podido actualizar los datos del ejemplo en la base de datos',
        'source': {'class': 'ModelDataManager', 'method': 'enable_analyzer_exception'},
        'log': None
    },
    'E-0114': {
        'description': 'El modelo solicitado no existe',
        'source': {'class': 'ModelManagerController', 'method': 'disable_analyzer_exception'},
        'log': 'L-0077'
    },
    'E-0115': {
        'description': 'La excepción no existe o ya se encuentra deshabilitada',
        'source': {'class': 'ModelManagerController', 'method': 'disable_analyzer_exception'},
        'log': 'L-0078'
    },
    'E-0116': {
        'description': 'No se han podido actualizar los datos del ejemplo en la base de datos',
        'source': {'class': 'ModelDataManager', 'method': 'disable_analyzer_exception'},
        'log': None
    },
    'E-0117': {
        'description': 'Error al acceder a la colleción de ids autoincrementales',
        'source': {'class': '', 'method': 'db_get_autoincremental_id'},
        'log': None
    },
    'E-0118': {
        'description': 'El modelo a importar ya existe',
        'source': {'class': 'ModelManagerController', 'method': 'import_model'},
        'log': 'L-0128'
    },
    'E-0119': {
        'description': 'Error al obtener el modelo remoto',
        'source': {'class': 'ModelManagerController', 'method': 'import_model'},
        'log': 'L-0170'
    },
    'E-0120': {
        'description': 'Error al descomprimir los archivos de modelo',
        'source': {'class': '', 'method': 'unzip_model'},
        'log': 'L-0099'
    },
    'E-0121': {
        'description': 'Error al comprimir el modelo',
        'source': {'class': '', 'method': 'zip_model'},
        'log': 'L-0203'
    },
    'E-0122': {
        'description': 'El modelo a exportar no existe',
        'source': {'class': 'ModelManagerController', 'method': 'export_model'},
        'log': 'L-0206'
    }
}
