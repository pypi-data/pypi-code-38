from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from ...database import db_session
from ...utils.utils import update_model
from ...resources.Patent.models import PatentModel
from .schemas import (
    PatentResourceSchema,
    PatentQueryParamsSchema,
)
from marshmallow import ValidationError


schema_resource = PatentResourceSchema()
schema_params = PatentQueryParamsSchema()


class DBException(SQLAlchemyError):
    pass


class PatentNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class Patent:
    @staticmethod
    def create(params):
        """
        :param
            Dict: PatentResourceSchema
        :return:
            PatentResourceSchema
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
            params: PatentQueryParamsSchema
        :return:
            List<PatentResourceSchema>
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
            params: PatentQueryParamsSchema
        :return:
            PatentResourceSchema
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        patent_query = _build_query(params=data).one()
        response = schema_resource.dump(patent_query).data
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

        patent_query = db_session.query(PatentModel).filter_by(id=id).first()
        if not patent_query:
            raise PatentNotFoundException('Patent does not exist!')
        try:
            db_session.delete(patent_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise DBException('DB error')

    @staticmethod
    def upsert(params):
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        patent_query = db_session.query(PatentModel).filter_by(
            patent_number=params.get('patent_number'),
            jurisdiction=params.get('jurisdiction'),
        ).first()

        if not patent_query:
            response = _helper_create(data)
        else:
            response = _helper_update(data, patent_query)
        return response

    @staticmethod
    def pharma_patents():
        # pharma patents have app_grp_art_number in the 1600s
        patent_query = db_session.query(PatentModel).filter(
            PatentModel.app_grp_art_number.op('regexp')('^16\d\d$'))
        response = schema_resource.dump(patent_query, many=True).data
        return response


def _helper_create(data):
    new_patent = PatentModel(
        updated_at=datetime.utcnow(),
        **data,
    )
    try:
        db_session.add(new_patent)
        db_session.commit()
        patent_query = db_session.query(PatentModel).get(new_patent.id)
        response = schema_resource.dump(patent_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, patent_query):
    data['id'] = patent_query.id
    data['patent_number'] = patent_query.patent_number
    data['jurisdiction'] = patent_query.jurisdiction
    try:
        update_model(data, patent_query)
        db_session.commit()
        response = schema_resource.dump(patent_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(PatentModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('patent_number'):
        q = q.filter_by(patent_number=params.get('patent_number'))
    if params.get('jurisdiction'):
        q = q.filter_by(jurisdiction=params.get('jurisdiction'))
    if params.get('app_grp_art_number'):
        q = q.filter_by(app_grp_art_number=params.get('app_grp_art_number'))
    if params.get('primary_identifier'):
        q = q.filter_by(primary_identifier=params.get('primary_identifier'))
    return q
