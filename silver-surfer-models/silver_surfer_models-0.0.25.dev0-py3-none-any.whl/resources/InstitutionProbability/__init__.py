from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from ...database import db_session
from ...resources.InstitutionProbability.models import (
    InstitutionProbabilityModel,
)
from .schemas import (
    InstitutionProbabilityResourceSchema,
    InstitutionProbabilityQueryParamsSchema,
)
from ...utils.utils import update_model


schema_resource = InstitutionProbabilityResourceSchema()
schema_params = InstitutionProbabilityQueryParamsSchema()


class InstitutionProbability(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(InstitutionProbabilityResourceSchema)

        Returns: InstitutionProbabilityResourceSchema

        Raises:
            ValidationError
            SQLAlchemyError
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
            params: dict(InstitutionProbabilityQueryParamsSchema)

        Returns: List<InstitutionProbabilityResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        institution_probability_query = _build_query(params=data)
        response = schema_resource.dump(
            institution_probability_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(InstitutionProbabilityQueryParamsSchema)

        Returns: InstitutionProbabilityResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        institution_probability_query = _build_query(params=data).one()
        response = schema_resource.dump(institution_probability_query).data
        return response

    @staticmethod
    def upsert(params):
        """
        Args:
            params: InstitutionProbabilityResourceSchema

        Returns:
            InstitutionProbabilityResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'ptab_trial_num': params['ptab_trial_num'],
            }
            institution_probability_query = _build_query(query_params).one()
            response = _helper_update(data, institution_probability_query)
        except NoResultFound:
            response = _helper_create(data)
        return response


def _helper_create(data):
    new_institution_probability = InstitutionProbabilityModel(**data)
    try:
        db_session.add(new_institution_probability)
        db_session.commit()
        institution_probability_query = db_session.query(
            InstitutionProbabilityModel).get(
            new_institution_probability.id)
        response = schema_resource.dump(institution_probability_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, institution_probability_query):
    data['id'] = institution_probability_query.id
    data['ptab_trial_num'] = institution_probability_query.ptab_trial_num
    try:
        update_model(data, institution_probability_query)
        db_session.commit()
        response = schema_resource.dump(institution_probability_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        InstitutionProbabilityModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('ptab_trial_num'):
        q = q.filter_by(
            ptab_trial_num=params.get('ptab_trial_num'))
    return q
