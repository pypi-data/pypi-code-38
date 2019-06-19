from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from marshmallow import ValidationError

from ...database import db_session
from .models import ProcessorResultTagModel
from .schemas import (
    ProcessorResultTagResourceSchema,
    ProcessorResultTagQueryParamsSchema,
)


schema_resource = ProcessorResultTagResourceSchema()
schema_params = ProcessorResultTagQueryParamsSchema()


class DBException(SQLAlchemyError):
    pass


class ProcessorResultTagNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class ProcessorResultTag:
    @staticmethod
    def create(params):
        """
        :param
            Dict
                document_id: int: required
                processor_result_id: int: required
                processor_name: string: required
                tag: string: required
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
                document_id
                processor_result_id
                processor_name
        :return:
            queried object
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        patent_query = _build_query(params=data)
        response = schema_resource.dump(patent_query, many=True).data
        return response

    @staticmethod
    def delete(id):
        """
        :param
            id
        :return:
            delete message
        :exception:
            PatentNotFoundException
            DBException
        """

        processor_result_tag_query = db_session.query(
            ProcessorResultTagModel).filter_by(
            id=id
        ).first()
        if not processor_result_tag_query:
            raise ProcessorResultTagNotFoundException(
                'Processor result tag does not exist!',
            )
        try:
            db_session.delete(processor_result_tag_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise DBException('DB error')


def _helper_create(data):
    new_processor_result_tag = ProcessorResultTagModel(
        document_id=data['document_id'],
        processor_result_id=data['processor_result_id'],
        processor_name=data['processor_name'],
        tag=data['tag'],
        updated_at=datetime.utcnow(),
    )
    try:
        db_session.add(new_processor_result_tag)
        db_session.commit()
        tag_query = db_session.query(
            ProcessorResultTagModel).get(
            new_processor_result_tag.id,
        )
        response = schema_resource.dump(tag_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise DBException('DB error')


def _build_query(params):
    q = db_session.query(
        ProcessorResultTagModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('document_id'):
        q = q.filter_by(document_id=params.get('document_id'))
    if params.get('processor_result_id'):
        q = q.filter_by(processor_result_id=params.get('processor_result_id'))
    if params.get('processor_name'):
        q = q.filter_by(processor_name=params.get('processor_name'))
    return q
