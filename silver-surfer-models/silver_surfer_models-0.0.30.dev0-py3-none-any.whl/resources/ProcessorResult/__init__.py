from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from marshmallow import ValidationError

from ...database import db_session
from .models import ProcessorResultModel
from .schemas import (
    ProcessorResultResourceSchema,
    ProcessorResultQueryParamsSchema,
)


schema_resource = ProcessorResultResourceSchema()
schema_params = ProcessorResultQueryParamsSchema()


class DBException(SQLAlchemyError):
    pass


class ProcessorResultNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class ProcessorResult:
    @staticmethod
    def create(params):
        """
        :param
            Dict
                document_id: int: required
                processor_name: string: required
                result: string: required
                additional_data: dict: required
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
            ProcessorResultNotFoundException
            DBException
        """

        processor_result_query = db_session.query(
            ProcessorResultModel).filter_by(
            id=id
        ).first()
        if not processor_result_query:
            raise ProcessorResultNotFoundException(
                'Processor result does not exist!',
            )
        try:
            db_session.delete(processor_result_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise DBException('DB error')


def _helper_create(data):
    new_processor_result = ProcessorResultModel(
        document_id=data['document_id'],
        processor_name=data['processor_name'],
        result=data['result'],
        updated_at=datetime.utcnow(),
    )
    try:
        db_session.add(new_processor_result)
        db_session.commit()
        patent_query = db_session.query(
            ProcessorResultModel).get(new_processor_result.id)
        response = schema_resource.dump(patent_query).data
        db_session.close()
        return response
    except SQLAlchemyError as e:
        db_session.rollback()
        db_session.close()
        print(e)
        raise DBException('DB error')


def _build_query(params):
    q = db_session.query(
        ProcessorResultModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('document_id'):
        q = q.filter_by(document_id=params.get('document_id'))
    if params.get('processor_name'):
        q = q.filter_by(processor_name=params.get('processor_name'))
    return q
