# @Vendors
from schema import Schema, And

# @Constants
from nlp_model_gen.constants.constants import (TOKEN_RULES_GEN_TYPE_NOUN, TOKEN_RULES_GEN_TYPE_VERB)

model_seed_schema = Schema({
    'nouns': {
        str: {
            'name': And(str, len), 
            'alert_message': And(str, len),
            'default_dir': And(str, len), 
            'type': And(str, lambda s: s == TOKEN_RULES_GEN_TYPE_NOUN), 
            'dictionary': And([And(str, len)], len)
        }
    },
    'verbs': {
        str: {
            'name': And(str, len), 
            'alert_message': And(str, len),
            'default_dir': And(str, len), 
            'type': And(str, lambda s: s == TOKEN_RULES_GEN_TYPE_VERB), 
            'dictionary': And([And(str, len)], len)
        }
    }
})

def validate_model_seed(model_seed):
    return model_seed_schema.is_valid(model_seed)
