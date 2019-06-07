from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from ...database import db_session
from ...resources.PTAB2Proceeding.models import PTAB2ProceedingModel
from .schemas import (
    PTAB2ProceedingResourceSchema,
    PTAB2ProceedingQueryParamsSchema,
)
from ...utils.utils import update_model


schema_resource = PTAB2ProceedingResourceSchema()
schema_params = PTAB2ProceedingQueryParamsSchema()


class PTAB2Proceeding(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: Dict (PTAB2ProceedingResourceSchema)

        Returns:
            PTAB2ProceedingResourceSchema

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
            params: PTAB2ProceedingQueryParamsSchema

        Returns:
            List<PTAB2ProceedingResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        ptab2_proceeding_query = _build_query(params=data)
        response = schema_resource.dump(ptab2_proceeding_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: PTAB2ProceedingQueryParamsSchema

        Returns:
            PTAB2ProceedingResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        ptab2_proceeding_query = _build_query(params=data).one()
        response = schema_resource.dump(ptab2_proceeding_query).data
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
        ptab2_proceeding_query = db_session.query(
            PTAB2ProceedingModel).filter_by(id=id).one()
        try:
            db_session.delete(ptab2_proceeding_query)
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
            params: PTAB2ProceedingResourceSchema

        Returns:
            PTAB2ProceedingResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'proceeding_number': params['proceeding_number'],
            }
            ptab2_proceeding_query = _build_query(query_params).one()
            response = _helper_update(data, ptab2_proceeding_query)
        except NoResultFound:
            response = _helper_create(data)
        return response

    @staticmethod
    def update(params):
        """
        Args:
            params: PTAB2ProceedingResourceSchema

        Returns:
            PTAB2ProceedingResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        query_params = {
            'proceeding_number': params['proceeding_number'],
        }
        ptab2_proceeding_query = _build_query(query_params).one()
        response = _helper_update(data, ptab2_proceeding_query)
        return response


def _helper_create(data):
    new_ptab2_proceeding = PTAB2ProceedingModel(**data)
    try:
        db_session.add(new_ptab2_proceeding)
        db_session.commit()
        ptab2_proceeding_query = db_session.query(
            PTAB2ProceedingModel).get(new_ptab2_proceeding.id)
        response = schema_resource.dump(ptab2_proceeding_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, ptab2_proceeding_query):
    data['id'] = ptab2_proceeding_query.id
    data['proceeding_number'] = ptab2_proceeding_query.proceeding_number
    try:
        update_model(data, ptab2_proceeding_query)
        db_session.commit()
        response = schema_resource.dump(ptab2_proceeding_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        PTAB2ProceedingModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('proceeding_number'):
        q = q.filter_by(proceeding_number=params.get('proceeding_number'))
    return q
