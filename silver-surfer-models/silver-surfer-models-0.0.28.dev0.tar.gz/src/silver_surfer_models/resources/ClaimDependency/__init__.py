from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from ...database import db_session
from ...resources.ClaimDependency.models import (
    ClaimDependencyModel,
)
from .schemas import (
    ClaimDependencyResourceSchema,
    ClaimDependencyQueryParamsSchema,
)
from marshmallow import ValidationError


schema_resource = ClaimDependencyResourceSchema()
schema_params = ClaimDependencyQueryParamsSchema()


class DBException(SQLAlchemyError):
    pass


class ClaimDependencyNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class ClaimDependency:
    @staticmethod
    def create(params):
        """
        :param
            Dict
                claim_id: int
                parent_claim_id: int
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
                claim_id
                parent_claim_id
        :return:
            queried object
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        claim_dependency_query = _build_query(params=data)
        response = schema_resource.dump(claim_dependency_query, many=True).data
        return response

    @staticmethod
    def delete(id):
        """
        :param
            id
        :return:
            delete message
        :exception:
            ClaimDependencyNotFoundException
            DBException
        """

        claim_dependency_query = db_session.query(
            ClaimDependencyModel).filter_by(
            id=id).first()
        if not claim_dependency_query:
            raise ClaimDependencyNotFoundException(
                'Claim dependency does not exist!')
        try:
            db_session.delete(claim_dependency_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise DBException('DB error')


def _helper_create(data):
    new_claim_dependency = ClaimDependencyModel(
        claim_id=data['claim_id'],
        parent_claim_id=data['parent_claim_id'],
        updated_at=datetime.utcnow(),
    )
    try:
        db_session.add(new_claim_dependency)
        db_session.commit()
        claim_dependency_query = db_session.query(
            ClaimDependencyModel).get(
            new_claim_dependency.id)
        response = schema_resource.dump(claim_dependency_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _build_query(params):
    q = db_session.query(ClaimDependencyModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('claim_id'):
        q = q.filter_by(claim_id=params.get('claim_id'))
    if params.get('parent_claim_id'):
        q = q.filter_by(parent_claim_id=params.get('parent_claim_id'))
    return q
