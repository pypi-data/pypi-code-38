from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from marshmallow import ValidationError

from ...database import db_session
from ...resources.File.models import FileModel
from .schemas import (
    FileResourceSchema,
    FileQueryParamsSchema,
    FilePatchSchema,
)
from ...utils.utils import update_model


schema_resource = FileResourceSchema()
schema_params = FileQueryParamsSchema()
schema_patch = FilePatchSchema()


class DBException(SQLAlchemyError):
    pass


class FileNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class File:
    @staticmethod
    def create(params):
        """
        :param
            Dict
                file_format
                s3_bucket_name
                s3_key_name
        :return:
            newly created object
        :exception:
            ValidationError
            DBException
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_create(data)
        return response

    @staticmethod
    def read(params):
        """
        :param
            params: dict
                id
                file_format
                s3_bucket_name
                s3_key_name
        :return:
            queried object
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        file_query = _build_query(params=data)
        response = schema_resource.dump(file_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        :param
            params: dict
                id
                file_format
                s3_bucket_name
                s3_key_name
        :return:
            queried object
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        file_query = _build_query(params=data).one()
        response = schema_resource.dump(file_query).data
        return response

    @staticmethod
    def update(id, params):
        """
        :param
            id: integer: required
            params: dict
                file_format
                s3_bucket_name
                s3_key_name
        :return:
            newly updated object
        :exception:
            FileNotFoundException
            ValidationError
            DBException
        """
        file_query = db_session.query(FileModel).filter_by(id=id).first()
        if not file_query:
            raise FileNotFoundException('Document not found!')
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, file_query)
        return response

    @staticmethod
    def delete(id):
        """
        :param
            id
        :return:
            delete message
        :exception:
            FileNotFoundException
            DBException
        """

        file_query = db_session.query(FileModel).filter_by(id=id).first()
        if not file_query:
            raise FileNotFoundException('File does not exist!')
        try:
            db_session.delete(file_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise DBException('DB error')

    @staticmethod
    def create_if_does_not_exist(params):
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        file_query = db_session.query(FileModel).filter_by(
            s3_bucket_name=data.get('s3_bucket_name'),
            s3_key_name=data.get('s3_key_name'),
        ).first()

        if not file_query:
            response = _helper_create(data)
        else:
            response = schema_resource.dump(file_query).data
        return response


def _helper_create(data):
    new_file = FileModel(
        file_format=data['file_format'],
        s3_bucket_name=data['s3_bucket_name'],
        s3_key_name=data['s3_key_name'],
        updated_at=datetime.utcnow(),
    )
    try:
        db_session.add(new_file)
        db_session.commit()
        file_query = db_session.query(FileModel).get(new_file.id)
        response = schema_resource.dump(file_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise DBException('DB error')


def _helper_update(data, document_query):
    data['id'] = document_query.id
    data['updated_at'] = datetime.utcnow()
    try:
        update_model(data, document_query)
        db_session.commit()
        response = schema_resource.dump(document_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise DBException('DB error')


def _build_query(params):
    q = db_session.query(FileModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('file_format'):
        q = q.filter_by(file_format=params.get('file_format'))
    if params.get('s3_bucket_name'):
        q = q.filter_by(s3_bucket_name=params.get('s3_bucket_name'))
    if params.get('s3_key_name'):
        q = q.filter_by(s3_key_name=params.get('s3_key_name'))
    return q
