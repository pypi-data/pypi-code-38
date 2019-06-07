from sqlalchemy.exc import SQLAlchemyError

from ...database import db_session
from ...resources.Claim.models import ClaimModel
from .schemas import (
    ClaimResourceSchema,
    ClaimQueryParamsSchema,
    ClaimPatchSchema,
)
from marshmallow import ValidationError


schema_resource = ClaimResourceSchema()
schema_params = ClaimQueryParamsSchema()
schema_patch = ClaimPatchSchema()


class DBException(SQLAlchemyError):
    pass


class ClaimNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class Claim:
    @staticmethod
    def create(params):
        """
        :param
            Dict
                patent_id: int
                claim_number: int
                claim_text: string
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
                patent_id
        :return:
            queried object
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        claim_query = _build_query(params=data)
        response = schema_resource.dump(claim_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
            :param
                params: dict
                    id
                    patent_id
            :return:
                queried object
            :exception:
                ValidationError
            """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        claim_query = _build_query(params=data).one()
        response = schema_resource.dump(claim_query).data
        return response

    @staticmethod
    def delete(id):
        """
        :param
            id
        :return:
            delete message
        :exception:
            ClaimNotFoundException
            DBException
        """

        claim_query = db_session.query(ClaimModel).filter_by(id=id).one()
        try:
            db_session.delete(claim_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise


def _helper_create(data):
    new_claim = ClaimModel(**data)
    try:
        db_session.add(new_claim)
        db_session.commit()
        claim_query = db_session.query(ClaimModel).get(new_claim.id)
        response = schema_resource.dump(claim_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _build_query(params):
    q = db_session.query(ClaimModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('patent_id'):
        q = q.filter_by(patent_id=params.get('patent_id'))
    if params.get('patent_application_id'):
        q = q.filter_by(
            patent_application_id=params.get('patent_application_id'))
    if params.get('claim_number'):
        q = q.filter_by(claim_number=params.get('claim_number'))
    return q
