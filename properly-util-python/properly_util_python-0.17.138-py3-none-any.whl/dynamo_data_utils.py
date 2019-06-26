
from properly_util_python import helper_utils


class DynamoData:

    @classmethod
    def to_dict(cls, dynamo_data):

       return helper_utils.dynamo_to_dict(dynamo_data)

    @classmethod
    def from_dict(cls, generic_dict):

        return helper_utils.dict_to_dynamo(generic_dict)
