# @Vendors
from schema import Schema, And, Use, Optional

# @Constants
from nlp_model_gen.constants.constants import TRAIN_MANAGER_SCHEMAS

custom_entity_tag_schema = Schema({
    'name': And(str, len),
    'description': And(str, len)
})

train_example_data_schema = Schema({
    'sentence': And(str, len),
    'type': And(str, len),
    Optional('tags'): [{
        'entity': And(str, len),
        'i_pos': And(Use(int)),
        'e_pos': And(Use(int))
    }]
})

schemas = dict({})
schemas[TRAIN_MANAGER_SCHEMAS['CUSTOM_ENTITY']] = custom_entity_tag_schema
schemas[TRAIN_MANAGER_SCHEMAS['TRAIN_DATA']] = train_example_data_schema

def validate_data(schema_key, data):
    if not schema_key in schemas.keys():
        return False
    return schemas[schema_key].is_valid(data)
