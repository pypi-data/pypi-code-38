from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from ...database import db_session
from ...resources.PatentApplication.models import (
    PatentApplicationModel,
)
from .schemas import (
    PatentApplicationResourceSchema,
    PatentApplicationQueryParamsSchema,
)
from ...utils.utils import update_model


schema_resource = PatentApplicationResourceSchema()
schema_params = PatentApplicationQueryParamsSchema()


class PatentApplication:
    @staticmethod
    def create(params):
        """
        Args:
            params: Dict (PatentApplicationResourceSchema)

        Returns:
            PatentApplicationResourceSchema

        Raises:
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
        Args:
            params: PatentApplicationQueryParamsSchema

        Returns:
            List<PatentApplicationResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        patent_application_query = _build_query(params=data)
        response = schema_resource.dump(
            patent_application_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: PatentApplicationQueryParamsSchema

        Returns:
            PatentApplicationResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        patent_application_query = _build_query(params=data).one()
        response = schema_resource.dump(patent_application_query).data
        return response

    @staticmethod
    def delete(id):
        """
        :param
            id
        :return:
            delete message
        :exception:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            SQLAlchemyError
        """

        patent_application_query = db_session.query(
            PatentApplicationModel).filter_by(
            id=id,
        ).one()
        try:
            db_session.delete(patent_application_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise

    @staticmethod
    def upsert(params):
        """
        Args:
            params: PatentApplicationResourceSchema

        Returns:
            PatentApplicationResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'application_number': params['application_number'],
                'jurisdiction': params['jurisdiction'],
            }
            patent_application_query = _build_query(query_params).one()
            response = _helper_update(data, patent_application_query)
        except NoResultFound:
            response = _helper_create(data)
        return response


def _helper_create(data):
    new_patent_application = PatentApplicationModel(**data)
    try:
        db_session.add(new_patent_application)
        db_session.commit()
        patent_application_query = db_session.query(
            PatentApplicationModel).get(
            new_patent_application.id)
        response = schema_resource.dump(patent_application_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, patent_application_query):
    data['id'] = patent_application_query.id
    data['application_number'] = patent_application_query.application_number
    data['jurisdiction'] = patent_application_query.jurisdiction
    try:
        update_model(data, patent_application_query)
        db_session.commit()
        response = schema_resource.dump(patent_application_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        PatentApplicationModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('application_number'):
        q = q.filter_by(application_number=params.get('application_number'))
    if params.get('jurisdiction'):
        q = q.filter_by(jurisdiction=params.get('jurisdiction'))
    return q
