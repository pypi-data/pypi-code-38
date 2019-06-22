from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from marshmallow import ValidationError

from ...database import db_session
from ...resources.PatentCompound.models import (
    PatentCompoundModel,
)
from .schemas import (
    PatentCompoundResourceSchema,
    PatentCompoundQueryParamsSchema,
)


schema_resource = PatentCompoundResourceSchema()
schema_params = PatentCompoundQueryParamsSchema()


class DBException(SQLAlchemyError):
    pass


class PatentCompoundNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class PatentCompound:
    @staticmethod
    def create(params):
        """
        :param
            Dict: PatentCompoundResourceSchema
        :return:
            PatentCompoundResourceSchema
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
            params: PatentCompoundQuerySchema
        :return:
            List<PatentCompoundResourceSchema>
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
            params: PatentCompoundQuerySchema
        :return:
            PatentCompoundResourceSchema
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
    new_patent = PatentCompoundModel(
        updated_at=datetime.utcnow(),
        **data,
    )
    try:
        db_session.add(new_patent)
        db_session.commit()
        patent_query = db_session.query(
            PatentCompoundModel).get(new_patent.id)
        response = schema_resource.dump(patent_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _build_query(params):
    q = db_session.query(PatentCompoundModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('patent_id'):
        q = q.filter_by(patent_id=params.get('patent_id'))
    if params.get('cid'):
        q = q.filter_by(cid=params.get('cid'))
    if params.get('compound_name'):
        q = q.filter_by(compound_name=params.get('compound_name'))
    if params.get('iupac_name'):
        q = q.filter_by(iupac_name=params.get('iupac_name'))

    return q
