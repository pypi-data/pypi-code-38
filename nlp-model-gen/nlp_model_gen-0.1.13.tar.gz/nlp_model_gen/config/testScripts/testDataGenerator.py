# @Utils
from nlp_model_gen.utils.fileUtils import load_json_file

# @Base
from nlp_model_gen.base import CURRENT_BASE_PATH

def get_conjugator_test_configs():
    data = load_json_file(CURRENT_BASE_PATH + '/config/resources/configurationTemplates.json')
    return {
        'conjugator_config': data['conjugator_cfg_template'],
        'exceptions_config': data['exception_cfg_template'],
        'fuzzy_generator_config': data['fuzzy_terms_generator_cfg_template'],
        'noun_conversor_config': data['noun_conversor_cfg_template'],
        'irregular_verbs_config': data['irregular_cfg_template']
    }
