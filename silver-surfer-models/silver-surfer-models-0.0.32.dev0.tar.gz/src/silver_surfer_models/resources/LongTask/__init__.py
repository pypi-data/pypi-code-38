from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from marshmallow import ValidationError

from ...database import db_session
from ...utils.utils import update_model
from ...resources.LongTask.models import LongTaskModel
from .schemas import (
    LongTaskResourceSchema,
    LongTaskQueryParamsSchema,
    LongTaskPatchSchema,
)


schema_resource = LongTaskResourceSchema()
schema_params = LongTaskQueryParamsSchema()
schema_patch = LongTaskPatchSchema()


class DBException(SQLAlchemyError):
    pass


class LongTaskNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class LongTask:
    @staticmethod
    def create(params):
        """
        :param
            Dict
                trial_id: int
                name: string
                state: string
                progress: float
                celery_task_id: string
                result: string
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
                trial_id
                name
                state
                celery_task_id
        :return:
            queried object
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        long_task_query = _build_query(params=data)
        response = schema_resource.dump(long_task_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
            :param
                params: dict
                    id
                    trial_id
                    name
                    state
                    celery_task_id
            :return:
                queried object
            :exception:
                ValidationError
            """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        long_task_query = _build_query(params=data).one()
        response = schema_resource.dump(long_task_query).data
        return response

    @staticmethod
    def update(id, params):
        """
        :param
            id: integer: required
            params: dict
                state: string
                progress: float
                result: string
        :return:
            newly updated object
        :exception:
            LongTaskNotFoundException
            ValidationError
            DBException
        """
        long_task_query = db_session.query(
            LongTaskModel).filter_by(id=id).first()
        if not long_task_query:
            raise LongTaskNotFoundException('LongTask not found!')
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, long_task_query)
        return response

    @staticmethod
    def delete(id):
        """
        :param
            id
        :return:
            delete message
        :exception:
            LongTaskNotFoundException
            DBException
        """

        long_task_query = db_session.query(
            LongTaskModel).filter_by(id=id).first()
        if not long_task_query:
            raise LongTaskNotFoundException('LongTask does not exist!')
        try:
            db_session.delete(long_task_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise DBException('DB error')


def _helper_create(data):
    new_long_task = LongTaskModel(
        trial_id=data['trial_id'],
        name=data['name'],
        state=data['state'],
        progress=data['progress'],
        celery_task_id=data['celery_task_id'],
        result=data.get('result', ''),
        updated_at=datetime.utcnow(),
    )
    try:
        db_session.add(new_long_task)
        db_session.commit()
        long_task_query = db_session.query(
            LongTaskModel).get(new_long_task.id)
        response = schema_resource.dump(long_task_query).data
        db_session.close()
        return response
    except SQLAlchemyError as err:
        db_session.rollback()
        db_session.close()
        raise DBException(err)


def _helper_update(data, long_task_query):
    data['id'] = long_task_query.id
    data['trial_id'] = long_task_query.trial_id
    data['name'] = long_task_query.name
    data['celery_task_id'] = long_task_query.celery_task_id
    data['updated_at'] = datetime.utcnow()
    try:
        update_model(data, long_task_query)
        db_session.commit()
        response = schema_resource.dump(long_task_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise DBException('DB error')


def _build_query(params):
    q = db_session.query(
        LongTaskModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('trial_id'):
        q = q.filter_by(trial_id=params.get('trial_id'))
    if params.get('name'):
        q = q.filter_by(name=params.get('name'))
    if params.get('state'):
        q = q.filter_by(state=params.get('state'))
    if params.get('celery_task_id'):
        q = q.filter_by(celery_task_id=params.get('celery_task_id'))
    return q
