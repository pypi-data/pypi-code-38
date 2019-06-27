import uuid
from typing import Union

from bson import binary

from .bottle_kit import ValidationError


def validate_payload_required_fields(payload: dict = None, required_fields: list = None, allow_null: bool = False):
    """
    Util method used to check if required field list are all including in payload data, allow_null means accept None value 
    """
    payload = payload or {}
    required_fields = required_fields or []

    for key in required_fields:
        if key not in payload:
            raise ValidationError({"msg": "Required field: <{}> is missing!".format(key)})
        elif not allow_null and not payload.get(key):
            raise ValidationError({"msg": "Required field: <{}> can not be <null> !".format(key)})

    return True


def build_mongodb_uuid_legacy(uuid_obj: uuid.UUID = None) -> binary.Binary:
    """
    **DEPRECATED**
    Create a python compatible mongo UUID object
    """
    uuid_obj = uuid_obj or uuid.uuid4()
    if not isinstance(uuid_obj, uuid.UUID):
        raise TypeError('uuid_obj must be an instance of uuid.UUID!')
    return binary.Binary(uuid_obj.bytes, binary.PYTHON_LEGACY)


def build_mongodb_uuid(uuid_obj: Union[uuid.UUID, binary.Binary] = None) -> binary.Binary:
    """
    Create a mongodb compatible UUID object which is a Binary instance with subtype=STANDARD
    """
    if isinstance(uuid_obj, binary.Binary) and uuid_obj.subtype == binary.STANDARD:
        return uuid_obj
    uuid_obj = uuid_obj or uuid.uuid4()
    if not isinstance(uuid_obj, uuid.UUID):
        raise TypeError('uuid_obj must be an instance of uuid.UUID!')
    return binary.Binary(uuid_obj.bytes, binary.STANDARD)


def convert_py_uuid_to_mongodb_uuid(uuid_string: Union[str, uuid.UUID] = None):
    """
    Convert the a python UUID string/instance to mongodb UUID object
    """
    if isinstance(uuid_string, uuid.UUID):
        return build_mongodb_uuid(uuid_string)
    return build_mongodb_uuid(uuid.UUID(str(uuid_string)))


def convert_mongo_legacy_uuid_to_standard_uuid(mongo_uri=None, db_name='default', collection_name='default'):
    from pymongo import MongoClient
    documents = MongoClient(mongo_uri).get_database(db_name).get_collection(collection_name)
    count = 0
    for obj in documents.find({}, {'_id': True}):
        count += 1
        legacy_id = build_mongodb_uuid_legacy(obj['_id'])
        doc = documents.find_one({'_id': legacy_id})
        if not doc:
            continue
        standard_id = build_mongodb_uuid(obj['_id'])
        doc['_id'] = standard_id
        documents.insert_one(doc)
        documents.remove({'_id': legacy_id})


def dict_attr(obj: dict = None, attr_name: str = None):
    """
    Util method to fetch dict object's nested attribute by dot annotation name
    Example:
         obj={'type':'book', 'author':{'name':'test'}}

         # to get obj's author's name value, we can do
         author_name = dict_attr(obj, 'author.name')
    """
    if obj is None or attr_name is None:
        return None

    for name in attr_name.split('.'):
        obj = obj.get(name, None)
        if obj is None:
            return None

    return obj
