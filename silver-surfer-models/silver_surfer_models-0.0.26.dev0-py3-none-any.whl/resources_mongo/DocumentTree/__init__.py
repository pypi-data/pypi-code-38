from datetime import datetime
from marshmallow import ValidationError
from pymongo.errors import OperationFailure

from ...database import get_mongo_db_session
from .schemas import (
    DocumentTreeResourceSchema,
    DocumentTreeQueryParamsSchema,
    DocumentTreePatchSchema,
)


schema_resource = DocumentTreeResourceSchema()
schema_params = DocumentTreeQueryParamsSchema()
schema_patch = DocumentTreePatchSchema()


class DBException(OperationFailure):
    pass


class DocumentTreeNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class DocumentTree:
    @staticmethod
    def create(params):
        """
        Args:
            params: Dict
                file_id: int
                value: Dict

        Returns: Dict
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)
        response = _helper_create(data)
        return response

    @staticmethod
    def read(params):
        """
        Args:
            params: Dict
                file_id

        Returns:

        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        mongo_db_session = get_mongo_db_session()
        query = mongo_db_session.document_trees.find(params)
        response = schema_resource.dump(query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: Dict
                file_id

        Returns: Dict

        Exception:
            ValidationError
            DocumentTreeNotFoundException
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        mongo_db_session = get_mongo_db_session()
        query = mongo_db_session.document_trees.find_one(params)
        if query is None:
            raise DocumentTreeNotFoundException('File id not found!')
        response = schema_resource.dump(query).data
        return response

    @staticmethod
    def update(params):
        """
        :param
            params: dict
                file_id
                value
        :return:
            newly updated object
        :exception:
            DocumentTreeNotFoundException
            ValidationError
            DBException
        """
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)
        data['updated_at'] = datetime.utcnow()
        mongo_db_session = get_mongo_db_session()
        result = mongo_db_session.document_trees.find_one_and_update(
            filter={'file_id': data['file_id']},
            update={'$set': data},
            return_document=True,
        )
        if result is None:
            raise DocumentTreeNotFoundException('File id not found!')
        response = schema_resource.dump(result).data
        return response

    @staticmethod
    def delete(file_id):
        mongo_db_session = get_mongo_db_session()
        result = mongo_db_session.document_trees.find_one_and_delete(
            filter={'file_id': file_id},
        )
        response = schema_resource.dump(result).data
        return response

    @staticmethod
    def update_or_create(params):
        """
        :param
            params: dict
                file_id
                value
        :return:
            newly updated/created object
        :exception:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)
        data['updated_at'] = datetime.utcnow()
        mongo_db_session = get_mongo_db_session()
        result = mongo_db_session.document_trees.find_one_and_update(
            filter={'file_id': data['file_id']},
            update={'$set': data},
            return_document=True,
            upsert=True,
        )
        response = schema_resource.dump(result).data
        return response


def _helper_create(data):
    try:
        data['updated_at'] = datetime.utcnow()
        mongo_db_session = get_mongo_db_session()
        mongo_db_session.document_trees.insert_one(data)
        return data['file_id']
    except Exception:
        raise DBException('DB error')
