from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from ...database import db_session
from ...resources.PTAB2Decision.models import PTAB2DecisionModel
from .schemas import (
    PTAB2DecisionResourceSchema,
    PTAB2DecisionQueryParamsSchema,
)
from ...utils.utils import update_model


schema_resource = PTAB2DecisionResourceSchema()
schema_params = PTAB2DecisionQueryParamsSchema()


class PTAB2Decision(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: Dict (PTAB2DecisionResourceSchema)

        Returns:
            PTAB2DecisionResourceSchema

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
            params: PTAB2DecisionQueryParamsSchema

        Returns:
            List<PTAB2DecisionResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        ptab2_decision_query = _build_query(params=data)
        response = schema_resource.dump(ptab2_decision_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: PTAB2DecisionQueryParamsSchema

        Returns:
            PTAB2DecisionResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        ptab2_decision_query = _build_query(params=data).one()
        response = schema_resource.dump(ptab2_decision_query).data
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
        ptab2_decision_query = db_session.query(
            PTAB2DecisionModel).filter_by(id=id).one()
        try:
            db_session.delete(ptab2_decision_query)
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
            params: PTAB2DecisionResourceSchema

        Returns:
            PTAB2DecisionResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'identifier': params['identifier'],
            }
            ptab2_decision_query = _build_query(query_params).one()
            response = _helper_update(data, ptab2_decision_query)
        except NoResultFound:
            response = _helper_create(data)
        return response


def _helper_create(data):
    new_ptab2_decision = PTAB2DecisionModel(**data)
    try:
        db_session.add(new_ptab2_decision)
        db_session.commit()
        ptab2_decision_query = db_session.query(
            PTAB2DecisionModel).get(new_ptab2_decision.id)
        response = schema_resource.dump(ptab2_decision_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, ptab2_decision_query):
    data['id'] = ptab2_decision_query.id
    data['identifier'] = ptab2_decision_query.identifier
    try:
        update_model(data, ptab2_decision_query)
        db_session.commit()
        response = schema_resource.dump(ptab2_decision_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        PTAB2DecisionModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('identifier'):
        q = q.filter_by(identifier=params.get('identifier'))
    return q
