ANALYZER_EXCEPTIONS_COLLECTION = 'analyzer_exceptions'
COMPOUNDING_START_DEFAULT = 4.0
COMPOUNDING_STOP_DEFAULT = 32.0
COMPOUNDING_COMPOUND_DEFAULT = 1.001
CUSTOM_ENTITY_MANAGER_COLLECTION = 'tm_custom_entities'
DB_CONNECTION_TIMEOUT = 3000
DB_GENERAL_SETTINGS_DB = 'nlp_general_settings'
DB_AUTOINCREMENTAL_ID_COL = 'autoincrement_id_col'
DB_OPERATION_DELETE = 'delete'
DB_OPERATION_DELETE_MANY = 'delete_many'
DB_OPERATION_INSERT = 'insert'
DB_OPERATION_INSERT_MANY = 'insert_many'
DB_OPERATION_UPDATE = 'update'
DB_SERVER_URL = 'mongodb://localhost:27017/'
DEFAULT_REPLACE_WILDCARD = '%s'
DIR_PATH_SEPARATOR = '/'
EVENT_MODEL_CREATED = 'event_model_created'
EVENT_MODEL_DELETED = 'event_model_deleted'
ERROR_GENERIC = 'Generic error'
LOGGER_WILDCARD = '%s'
MODEL_CONFIG_FILE_NAME = 'cfg.json'
MODEL_EXPORT_DEFAULT_SIZE = '20m'
MODEL_IMPORT_EXT = '.git'
MODEL_MANAGER_CUSTOM_FILES_DIR = 'custom_model_files'
MODEL_MANAGER_DB = 'model_manager_model_data'
MODEL_MANAGER_DEFAULT_BASE_MODEL = 'es_core_news_md'
MODEL_MANAGER_MODELS_COLLECTION = 'mm_models_data'
MODEL_MANAGER_ROOT_DIR = 'models'
MODEL_NER = 'ner'
MODEL_PACKAGING_EXTENSION = '.zip'
MODEL_PARTITION_EXTENSION = '.zip.p'
MODEL_TMP_JOINT_FILE_NAME = 'model_tmp.zip'
MODEL_TRAINING_DROP_RATE = 0.5
MODEL_TRAINING_ITER_AMOUNT = 50
PATH_SEPARATOR = '-'
STD_TIME_OUTPUT = "%Y-%m-%d %H:%M:%S"
TEXT_NOUNS = 'SUSTANTIVOS'
TEXT_VERBS = 'VERBOS'
TASK_KEYS_MODEL_UPDATE = 'model_update'
TASK_KEYS_WORD_PROCESSOR = 'word_processor'
TASK_STATUS_CANCELLED = 'cancelled'
TASK_STATUS_FINISHED = 'finished'
TASK_STATUS_QUEUED = 'queued'
TASK_STATUS_RUNNING = 'running'
TEXT_LENGTH_THRESHOLD = 999999
TOKEN_RULES_GEN_MODEL_SEED_FILENAME = 'model_seed.mdl'
TOKEN_RULES_GEN_NOUN = 'NOUN'
TOKEN_RULES_GEN_NOUN_SING_TAG = 'NOUN_BASE_SING'
TOKEN_RULES_GEN_NOUN_PLUR_TAG = 'NOUN_BASE_PLUR'
TOKEN_RULES_GEN_RULES_EXT = '.json'
TOKEN_RULES_GEN_TMP_ROOT_PATH = 'tmp'
TOKEN_RULES_GEN_TYPE_NOUN = 'noun'
TOKEN_RULES_GEN_TYPE_VERB = 'verb'
TOKEN_RULES_GEN_VERB = 'VERB'
TOKEN_RULES_GEN_VERB_GROUP_COMPLEX = [
    'VERB_%s_1STPER_SING',
    'VERB_%s_2NDPER_SING',
    'VERB_%s_3RDPER_SING',
    'VERB_%s_1STPER_PLUR',
    'VERB_%s_2NDPER_PLUR',
    'VERB_%s_3RDPER_PLUR'
]
TOKEN_RULES_GEN_VERB_GROUP_IMP = [
    'VERB_PRES_1STPER_PLUR',
    'VERB_%s_2NDPER_SING',
    'VERB_%s_3RDPER_SING',
    'VERB_%s_1STPER_PLUR',
    'VERB_%s_2NDPER_PLUR',
    'VERB_%s_3RDPER_PLUR'
]
TOKEN_RULES_GEN_VERB_GROUP_SIMPLE = ['%s']
TOKEN_RULES_GEN_VERB_GROUP_PART = ['%s', '%s', '%s']
TOKEN_RULES_GEN_VERB_CFG = {
    'inf': {'time_keys': ['VERB_INF'], 'tag_keys': TOKEN_RULES_GEN_VERB_GROUP_SIMPLE},
    'ger': {'time_keys': ['VERB_GER'], 'tag_keys': TOKEN_RULES_GEN_VERB_GROUP_SIMPLE},
    'part': {'time_keys': ['VERB_PART_MASC', 'VERB_PART_FEM', 'VERB_PART_MASC'], 'tag_keys': TOKEN_RULES_GEN_VERB_GROUP_PART},
    'pres': {'time_keys': ['PRES', 'PRES', 'PRES', 'PRES', 'PRES', 'PRES'], 'tag_keys': TOKEN_RULES_GEN_VERB_GROUP_COMPLEX},
    'pret_perf': {'time_keys': ['PAST', 'PAST', 'PAST', 'PAST', 'PAST', 'PAST'], 'tag_keys': TOKEN_RULES_GEN_VERB_GROUP_COMPLEX},
    'pret_imperf': {'time_keys': ['PAST', 'PAST', 'PAST', 'PAST', 'PAST', 'PAST'], 'tag_keys': TOKEN_RULES_GEN_VERB_GROUP_COMPLEX},
    'fut': {'time_keys': ['FUT', 'FUT', 'FUT', 'FUT', 'FUT', 'FUT'], 'tag_keys': TOKEN_RULES_GEN_VERB_GROUP_COMPLEX},
    'impA': {'time_keys': ['', 'IMP', 'IMP', 'IMP', 'IMP', 'IMP'], 'tag_keys': TOKEN_RULES_GEN_VERB_GROUP_IMP},
    'impB': {'time_keys': ['', 'IMP', 'IMP', 'IMP', 'IMP', 'IMP'], 'tag_keys': TOKEN_RULES_GEN_VERB_GROUP_IMP},
    'impC': {'time_keys': ['', 'IMP', 'IMP', 'IMP', 'IMP', 'IMP'], 'tag_keys': TOKEN_RULES_GEN_VERB_GROUP_IMP},
    'condA': {'time_keys': ['COND', 'COND', 'COND', 'COND', 'COND', 'COND'], 'tag_keys': TOKEN_RULES_GEN_VERB_GROUP_COMPLEX},
    'condB': {'time_keys': ['SIMP', 'SIMP', 'SIMP', 'SIMP', 'SIMP', 'SIMP'], 'tag_keys': TOKEN_RULES_GEN_VERB_GROUP_COMPLEX},
}
TOKENIZER_RESULTS_PLACEHOLDER = {'tokenizer_results': [], 'ner_results': []}
TRAIN_DATA_EXAMPLES_COLLECTION = 'tm_training_examples'
TRAIN_EXAMPLE_STATUS_APPLIED = 'applied'
TRAIN_EXAMPLE_STATUS_APPROVED = 'approved'
TRAIN_EXAMPLE_STATUS_REJECTED = 'rejected'
TRAIN_EXAMPLE_STATUS_SUBMITTED = 'submitted'
TRAIN_EXAMPLE_STATUS_HISTORIC = 'historic'
TRAIN_MANAGER_DB = 'train_manager_data'
TRAIN_MANAGER_SCHEMAS = {
    'CUSTOM_ENTITY': 'train_manager_entity_schema',
    'TRAIN_DATA': 'train_manager_example_data_schema'
}
TRAIN_MANAGER_SCHEMA_VALIDATION_ERROR = 'Error al validar estructura de los datos'
WORD_PROCESSOR_CONFIG_DB = 'word_processor_config'
WORD_PROCESSOR_CONJ_CFG_COLLECTION = 'wp_conjugator_config'
WORD_PROCESSOR_FUZZY_GEN_CFG_COLLECTION = 'wp_fuzzy_gen_config'
WORD_PROCESSOR_GENERAL_SETTING_COLLECTION = 'wp_general_settings'
WORD_PROCESSOR_MODULE_KEY_CONJUGATOR = 'conjugator'
WORD_PROCESSOR_MODULE_KEY_FUZZY_GEN = 'fuzzy_gen'
WORD_PROCESSOR_MODULE_KEY_NOUN_CONV = 'noun_conversor'
WORD_PROCESSOR_NOUN_CONV_CFG_COLLECTION = 'wp_noun_conv_config'
WORD_PROCESSOR_SPECIAL_CHARS = [('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ü', 'u')]
WORD_PROCESSOR_VERB_EXCEPTIONS_COLLECTION = 'wp_conjugator_verb_exceptions'
WORD_PROCESSOR_VERB_GROUPS_COLLECTION = 'wp_conjugator_verb_groups'
WORD_PROCESOR_DEFAULT_MODE = 0
WORD_PROCESSOR_DEFAULT_THEME = 'default'
WORD_PROCESOR_RESERVED_THEME = 'selected_theme'
WORD_PROCESSOR_SCHEMAS = {
    'CONJ_GENERAL_CFG': 'conjugator_general_config_schema',
    'CONJ_IRR_GROUPS': 'conjugator_verb_groups_schema ',
    'CONJ_EXCEPTIONS': 'conjugator_verb_exceptions_schema',
    'FUZZY_GENERAL_CFG': 'fuzzy_genetator_config_schema',
    'NOUN_CONV_GENERAL_CFG': 'noun_conversor_config_schema'
}
WORD_PROCESSOR_DEFAULT_CFG_OBJECT = {
    'conjugator_active_theme': 'default',
    'fuzzy_gen_active_theme': 'default',
    'noun_conversor_active_theme': 'default'
}
