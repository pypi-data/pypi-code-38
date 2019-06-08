# @Vendors
import random
import spacy
from spacy.util import minibatch, compounding
from git import Repo

# @Utils
from nlp_model_gen.utils.fileUtils import copy_dir, remove_files, unzip_model, zip_model

# @Logger
from nlp_model_gen.packages.logger.Logger import Logger
from nlp_model_gen.packages.logger.assets.logColors import ERROR_COLOR, HIGHLIGHT_COLOR, SUCCESS_COLOR

# @Error handler
from nlp_model_gen.packages.errorHandler.ErrorHandler import ErrorHandler

# @Utils
from nlp_model_gen.utils.fileUtils import (
    build_path, 
    check_dir_existence,
    copy_file,
    create_dir_if_not_exist,
    dictionary_to_disk,
    get_absoulute_path,
    load_json_file,
    remove_dir
)

# @Config
from nlp_model_gen.base import CURRENT_BASE_PATH

# @Constants
from nlp_model_gen.constants.constants import (
    COMPOUNDING_COMPOUND_DEFAULT,
    COMPOUNDING_START_DEFAULT,
    COMPOUNDING_STOP_DEFAULT,
    DIR_PATH_SEPARATOR,
    MODEL_CONFIG_FILE_NAME,
    MODEL_IMPORT_EXT,
    MODEL_MANAGER_CUSTOM_FILES_DIR,
    MODEL_MANAGER_DEFAULT_BASE_MODEL,
    MODEL_MANAGER_ROOT_DIR,
    MODEL_NER,
    MODEL_PACKAGING_EXTENSION,
    MODEL_TMP_JOINT_FILE_NAME,
    MODEL_TRAINING_DROP_RATE,
    MODEL_TRAINING_ITER_AMOUNT,
    TOKEN_RULES_GEN_MODEL_SEED_FILENAME
)

class ModelLoader:
    def __init__(self):
        pass

    @staticmethod
    def load_model(path):
        """
        Carga el modelo a partir del path.

        :path: [String] - Ruta para acceder al modelo.

        :return: [SpacyModelRef] - Referencia al modelo de spacy, None si no se pdo cargar el modelo.
        """
        try:
            full_path = build_path(MODEL_MANAGER_ROOT_DIR, path, add_absolute_root=True)
            nlp_model = spacy.load(full_path)
            return nlp_model
        except:
            ErrorHandler.raise_error('E-0092')

    @staticmethod
    def initiate_default_model():
        """
        Inicializa un instancia del modelo por defecto.
    
        :return: [SpacyModelRef] - Referencia al modelo de spacy
        """
        try:
            default_nlp_model = spacy.load(MODEL_MANAGER_DEFAULT_BASE_MODEL)
            return default_nlp_model
        except:
            ErrorHandler.raise_error('E-0028')

    @staticmethod
    def save_model(model, path, tmp_files_path, new_model):
        """
        Guarda el modelo en el path solicitado.

        :model: [SpacyModelRef] - Referencia a un modelo de spacy.

        :path: [String] - Ruta en la cual guardar el modelo.

        :tmp_files_path: [String] - Ruta donde se encuentran los archivos temporales del modelo.

        :new_model: [Model] - Objeto que representa el nuevo modelo.
        """
        Logger.log('L-0030')
        base_path = build_path(MODEL_MANAGER_ROOT_DIR, path)
        if check_dir_existence(base_path):
            ErrorHandler.raise_error('E-0030')
        model_storage_path = get_absoulute_path(base_path)
        model.to_disk(model_storage_path)
        custom_model_files_path = build_path(base_path, MODEL_MANAGER_CUSTOM_FILES_DIR)
        create_dir_if_not_exist(custom_model_files_path)
        model_seed_path = build_path(tmp_files_path, TOKEN_RULES_GEN_MODEL_SEED_FILENAME)
        model_seed_copy_path = build_path(custom_model_files_path, TOKEN_RULES_GEN_MODEL_SEED_FILENAME, add_absolute_root=True)
        copy_file(model_seed_path, model_seed_copy_path, is_absolute_path=True)
        cfg_file_path = build_path(model_storage_path, MODEL_CONFIG_FILE_NAME)
        dictionary_to_disk(cfg_file_path, {
            'model_name': new_model.get_model_name(),
            'description': new_model.get_description(),
            'author': new_model.get_author(),
            'analyzer_rule_set': new_model.get_analyser_rules_set()
        }, True)
        Logger.log('L-0032')

    @staticmethod
    def delete_model_files(path):
        """
        Elimina los archivos de un modelo del disco.

        :path: [String] - Ruta a eliminar.
        """
        Logger.log('L-0070')
        full_path = build_path(MODEL_MANAGER_ROOT_DIR, path)
        remove_dir(full_path)

    @staticmethod
    def get_model_ner(model_ref):
        """
        Obtiene el NER de un determinado modelo. Si el mismo no existe, crea uno nuevo y lo agrega
        al pipeline del modelo.

        :model_reference: [SpacyModelRef] - Referencia al modelo de spacy
        """
        Logger.log('L-0343')
        ner = None
        if MODEL_NER in model_ref.pipe_names:
            ner = model_ref.get_pipe(MODEL_NER)
        else:
            ner = model_ref.create_pipe(MODEL_NER)
            model_ref.add_pipe(ner, last=True)
        Logger.log('L-0344')
        return ner

    @staticmethod
    def add_ner_labels(ner, training_data):
        """
        Agrega las nuevas etiquetas al ner.

        :ner: [SpacyNER] - NER al cual aplicar las nuevas etiquetas

        :training_data: [List(Dict)] - Set de datos de entrenamiento.
        """
        Logger.log('L-0345')
        for _, annotations in training_data:
            for ent in annotations.get('entities'):
                ner.add_label(ent[2])
        Logger.log('L-0346')

    @staticmethod
    def apply_training_loop(model_ref, training_data):
        """
        Aplica el bucle de entrenamiento al NER de un determinado modelo.

        :model_ref: [SpacyModelRef] - Referencia del modelo de spacy

        :training_data: [List] - Set de datos de entrenamiento
        """
        for iter_number in range(1, MODEL_TRAINING_ITER_AMOUNT):
            Logger.log('L-0350', [{'text': iter_number, 'color': SUCCESS_COLOR}, {'text': MODEL_TRAINING_ITER_AMOUNT, 'color': HIGHLIGHT_COLOR}])
            random.shuffle(training_data)
            losses = {}
            batches = minibatch(training_data, size=compounding(COMPOUNDING_START_DEFAULT, COMPOUNDING_STOP_DEFAULT, COMPOUNDING_COMPOUND_DEFAULT))
            for batch in batches:
                texts, annotations = zip(*batch)
                model_ref.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=MODEL_TRAINING_DROP_RATE,  # dropout - make it harder to memorise data
                    losses=losses,
                )
            Logger.log('L-0351', [{'text': iter_number, 'color': SUCCESS_COLOR}, {'text': losses['ner'], 'color': HIGHLIGHT_COLOR}])
    
    @staticmethod
    def update_model_info(model_ref, model_path):
        """
        Actualiza la información en dico para el modelo que se encuentra en el path
        especificado.

        :model_ref: [SpacyModelRef] - Referencia del modelo de spacy

        :model_path: [String] - Directorio base del modelo (nombre del mismo).
        """
        Logger.log('L-0352')
        relative_base_path = build_path(MODEL_MANAGER_ROOT_DIR, model_path)
        relative_seed_path = build_path(MODEL_MANAGER_ROOT_DIR, model_path +  DIR_PATH_SEPARATOR + MODEL_MANAGER_CUSTOM_FILES_DIR)
        base_path = build_path(MODEL_MANAGER_ROOT_DIR, model_path, add_absolute_root=True)
        seed_dir_path = build_path(MODEL_MANAGER_ROOT_DIR, model_path +  DIR_PATH_SEPARATOR + MODEL_MANAGER_CUSTOM_FILES_DIR, add_absolute_root=True)
        cfg_file_path = build_path(MODEL_MANAGER_ROOT_DIR, model_path + DIR_PATH_SEPARATOR + MODEL_CONFIG_FILE_NAME, add_absolute_root=True)
        model_seed = load_json_file(build_path(seed_dir_path, TOKEN_RULES_GEN_MODEL_SEED_FILENAME))
        cfg = load_json_file(cfg_file_path)
        remove_dir(relative_base_path)
        create_dir_if_not_exist(relative_base_path)
        create_dir_if_not_exist(relative_seed_path)
        model_ref.to_disk(base_path)
        dictionary_to_disk(relative_seed_path + DIR_PATH_SEPARATOR + TOKEN_RULES_GEN_MODEL_SEED_FILENAME, model_seed)
        dictionary_to_disk(relative_base_path + DIR_PATH_SEPARATOR + MODEL_CONFIG_FILE_NAME, cfg)
        Logger.log('L-0353')

    @staticmethod
    def apply_training_data(model, training_data):
        """
        Ejecuta la rutina de entrenamiento de un modelo particular.

        :model: [Model] - Modelo sobre el cual aplicar el entrenamiento.

        :training_data: [List(Dict)] - Conjunto de datos de entrenamiento.
        """
        model_ref = model.get_reference()
        model_path = model.get_path()
        ner = ModelLoader.get_model_ner(model_ref)
        ModelLoader.add_ner_labels(ner, training_data)
        other_pipes = [pipe for pipe in model_ref.pipe_names if pipe != MODEL_NER]
        Logger.log('L-0347')
        with model_ref.disable_pipes(*other_pipes):
            ModelLoader.apply_training_loop(model_ref, training_data)
        ModelLoader.update_model_info(model_ref, model_path)
        Logger.log('L-0348')

    @staticmethod
    def import_model(model_id, source):
        """
        Obtiene los archivos de modelo, los descomprime y obtiene el diccionario de
        configuración del modelo remoto solicitado.

        :model_id: [String] - Id del modelo a importar.

        :return: [Dict] - Dicionario con la configuración del modelo.
        """
        try:
            local_path = '%s/%s/%s' % (CURRENT_BASE_PATH, MODEL_MANAGER_ROOT_DIR, model_id)
            model_cfg_file = '%s/%s' % (local_path, MODEL_CONFIG_FILE_NAME)
            if source['remote']:
                remote_repo_url = '%s/%s%s' % (source['path'], model_id, MODEL_IMPORT_EXT)
                Logger.log('L-0134', [{'text': remote_repo_url, 'color': HIGHLIGHT_COLOR}])
                Repo.clone_from(remote_repo_url, local_path)
            else:
                Logger.log('L-0140', [{'text': source['path'], 'color': HIGHLIGHT_COLOR}])
                copy_dir(source['path'], local_path)
            Logger.log('L-0147')
            Logger.log('L-0154')
            unzip_model(local_path, model_id)
            remove_files(local_path, '%s%s' % (model_id, MODEL_PACKAGING_EXTENSION))
            remove_files(local_path, '%s' % MODEL_TMP_JOINT_FILE_NAME)
            Logger.log('L-0161')
            return load_json_file(model_cfg_file)
        except Exception as e:
            ErrorHandler.raise_error('E-0119', [{'text': e, 'color': ERROR_COLOR}])

    @staticmethod
    def export_model(model, output_path, split):
        """
        Genera los archivos de configuración, comprime los archivos de modelo y los
        copia al directorio solicitado.

        :model: [Model] - Modelo a exportar.

        :output_path: [String] - Ruta absouluta en donde se quiere guardar el
        modelo.

        :split: [boolean] - Indica si se debe particionar el paquete del modelo
        """
        Logger.log('L-0221')
        cfg = model.to_dict()
        cfg['analyzer_exceptions_set'] = [exception.to_dict() for exception in model.get_analyzer_exceptions_set()]
        base_path = build_path(MODEL_MANAGER_ROOT_DIR, model.get_model_id(), add_absolute_root=True)
        relative_base_path = build_path(MODEL_MANAGER_ROOT_DIR, model.get_model_id() + DIR_PATH_SEPARATOR + MODEL_CONFIG_FILE_NAME)
        dictionary_to_disk(relative_base_path, cfg)
        Logger.log('L-0224')
        Logger.log('L-0246')
        zip_model(base_path, output_path, model.get_model_id(), split)
        Logger.log('L-0265')
