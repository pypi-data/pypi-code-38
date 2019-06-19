from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.operators import in_op
from datetime import datetime
from marshmallow import ValidationError

from ...database import db_session
from ...resources.Trial.models import TrialModel
from .schemas import (
    TrialResourceSchema,
    TrialQueryParamsSchema,
    TrialPatchSchema,
)
from ...utils.utils import update_model


schema_resource = TrialResourceSchema()
schema_params = TrialQueryParamsSchema()
schema_patch = TrialPatchSchema()


class DBException(SQLAlchemyError):
    pass


class TrialNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class Trial:
    @staticmethod
    def create(params):
        """
        :param
            TrialResourceSchema
        :return:
            TrialResourceSchema
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
            TrialQueryParamsSchema
        :return:
            List<TrialResourceSchema>
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        trial_query = _build_query(params=data)
        response = schema_resource.dump(trial_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: TrialQueryParamsSchema

        Returns: TrialResourceSchema
        Raises:
            ValidationError
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        trial_query = _build_query(params=data).one()
        response = schema_resource.dump(trial_query).data
        return response

    @staticmethod
    def update(id, params):
        """
        :param
            id: integer: required
            params: TrialPatchSchema
        :return:
            TrialResourceSchema
        :exception:
            TrialNotFoundException
            ValidationError
            DBException
        """
        trial_query = db_session.query(TrialModel).filter_by(id=id).first()
        if not trial_query:
            raise TrialNotFoundException('Trial not found!')
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, trial_query)
        return response

    @staticmethod
    def delete(id):
        """
        :param
            id
        :return:
            delete message
        :exception:
            TrialNotFoundException
            DBException
        """

        trial_query = db_session.query(TrialModel).filter_by(id=id).first()
        if not trial_query:
            raise TrialNotFoundException('Trial not found!')
        try:
            db_session.delete(trial_query)
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

        trial_query = db_session.query(TrialModel).filter_by(
            ptab_trial_num=params.get('ptab_trial_num'),
        ).first()

        if trial_query is None:
            response = _helper_create(data)
        else:
            response = _helper_update(data, trial_query)
        return response


def _helper_create(data):
    new_trial = TrialModel(
        updated_at=datetime.utcnow(),
        **data,
    )
    try:
        db_session.add(new_trial)
        db_session.commit()
        trial_query = db_session.query(TrialModel).get(new_trial.id)
        response = schema_resource.dump(trial_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, trial_query):
    data['id'] = trial_query.id
    data['updated_at'] = datetime.utcnow()
    try:
        update_model(data, trial_query)
        db_session.commit()
        response = schema_resource.dump(trial_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(TrialModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if 'ids' in params:
        q = q.filter(in_op(
            TrialModel.id,
            params['ids'],
        ))
    if params.get('ptab_trial_num'):
        q = q.filter_by(ptab_trial_num=params.get('ptab_trial_num'))
    if params.get('trial_filing_date'):
        q = q.filter_by(trial_filing_date=params.get('trial_filing_date'))
    if params.get('patent_num'):
        q = q.filter_by(patent_num=params.get('patent_num'))
    if 'patent_nums' in params:
        q = q.filter(in_op(
            TrialModel.patent_num,
            params.get('patent_nums'),
        ))
    if params.get('is_cleaned'):
        q = q.filter_by(is_cleaned=params.get('is_cleaned'))
    if params.get('is_processed'):
        q = q.filter_by(is_processed=params.get('is_processed'))
    return q
