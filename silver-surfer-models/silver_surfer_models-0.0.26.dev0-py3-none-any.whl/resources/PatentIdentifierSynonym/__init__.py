from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from marshmallow import ValidationError

from ...database import db_session
from ...resources.PatentIdentifierSynonym.models import (
    PatentIdentifierSynonymModel,
)
from .schemas import (
    PatentIdentifierSynonymResourceSchema,
    PatentIdentifierSynonymQueryParamsSchema,
)


schema_resource = PatentIdentifierSynonymResourceSchema()
schema_params = PatentIdentifierSynonymQueryParamsSchema()


class DBException(SQLAlchemyError):
    pass


class PatentIdentifierSynonymNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class PatentIdentifierSynonym:
    @staticmethod
    def create(params):
        """
        :param
            Dict: PatentIdentifierSynonymResourceSchema
        :return:
            PatentIdentifierSynonymResourceSchema
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
            params: PatentIdentifierSynonymQuerySchema
        :return:
            List<PatentIdentifierSynonymResourceSchema>
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
    def one(params):
        """
        :param
            params: PatentIdentifierSynonymQuerySchema
        :return:
            PatentIdentifierSynonymResourceSchema
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        patent_query = _build_query(params=data).one()
        response = schema_resource.dump(patent_query).data
        return response


def _helper_create(data):
    new_patent = PatentIdentifierSynonymModel(
        updated_at=datetime.utcnow(),
        **data,
    )
    try:
        db_session.add(new_patent)
        db_session.commit()
        patent_query = db_session.query(
            PatentIdentifierSynonymModel).get(new_patent.id)
        response = schema_resource.dump(patent_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _build_query(params):
    q = db_session.query(PatentIdentifierSynonymModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('patent_id'):
        q = q.filter_by(patent_id=params.get('patent_id'))
    if params.get('synonym'):
        q = q.filter_by(synonym=params.get('synonym'))
    return q
