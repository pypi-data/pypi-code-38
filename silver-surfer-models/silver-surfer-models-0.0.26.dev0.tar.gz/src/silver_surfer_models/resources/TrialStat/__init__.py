from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from ...database import db_session
from ...resources.TrialStat.models import (
    TrialStatModel,
)
from .schemas import (
    TrialStatResourceSchema,
    TrialStatQueryParamsSchema,
)
from ...utils.utils import update_model


schema_resource = TrialStatResourceSchema()
schema_params = TrialStatQueryParamsSchema()


class TrialStat(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(TrialStatResourceSchema)

        Returns: TrialStatResourceSchema

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
            params: dict(TrialStatQueryParamsSchema)

        Returns: List<TrialStatResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        trial_stat_query = _build_query(params=data)
        response = schema_resource.dump(
            trial_stat_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(TrialStatQueryParamsSchema)

        Returns: TrialStatResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        trial_stat_query = _build_query(params=data).one()
        response = schema_resource.dump(trial_stat_query).data
        return response

    @staticmethod
    def upsert(params):
        """
        Args:
            params: TrialStatResourceSchema

        Returns:
            TrialStatResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'stat_type': params['stat_type'],
                'name': params['name'],
            }
            trial_stat_query = _build_query(query_params).one()
            response = _helper_update(data, trial_stat_query)
        except NoResultFound:
            response = _helper_create(data)
        return response


def _helper_create(data):
    new_trial_stat = TrialStatModel(**data)
    try:
        db_session.add(new_trial_stat)
        db_session.commit()
        trial_stat_query = db_session.query(TrialStatModel).get(
            new_trial_stat.id)
        response = schema_resource.dump(trial_stat_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, trial_stat_query):
    data['id'] = trial_stat_query.id
    data['stat_type'] = trial_stat_query.stat_type
    data['name'] = trial_stat_query.name
    try:
        update_model(data, trial_stat_query)
        db_session.commit()
        response = schema_resource.dump(trial_stat_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        TrialStatModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('stat_type'):
        q = q.filter_by(
            stat_type=params.get('stat_type'))
    if params.get('name'):
        q = q.filter_by(
            name=params.get('name'))
    return q
