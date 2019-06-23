from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from marshmallow import ValidationError

from ...database import db_session
from ...utils.utils import update_model
from .models import PriorArtTempModel
from .schemas import (
    PriorArtTempResourceSchema,
    PriorArtTempQueryParamsSchema,
    PriorArtTempPatchSchema,
)


schema_resource = PriorArtTempResourceSchema()
schema_params = PriorArtTempQueryParamsSchema()
schema_patch = PriorArtTempPatchSchema()


class DBException(SQLAlchemyError):
    pass


class PriorArtTempNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class PriorArtTemp:
    @staticmethod
    def create(params):
        """
        :param
            Dict
                prior_art_id: int
                prior_art_detail: string
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
                prior_art_id
        :return:
            queried object
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        prior_art_temp_query = _build_query(params=data)
        response = schema_resource.dump(prior_art_temp_query, many=True).data
        return response

    @staticmethod
    def update(id, params):
        """
        :param
            id: integer: required
            params: dict
                prior_art_detail
        :return:
            newly updated object
        :exception:
            PriorArtNotFoundException
            ValidationError
            DBException
        """
        prior_art_temp_query = db_session.query(
            PriorArtTempModel).filter_by(id=id).first()
        if not prior_art_temp_query:
            raise PriorArtTempNotFoundException('Prior art temp not found!')
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, prior_art_temp_query)
        return response

    @staticmethod
    def delete(id):
        """
        :param
            id
        :return:
            delete message
        :exception:
            PriorArtNotFoundException
            DBException
        """

        prior_art_temp_query = db_session.query(
            PriorArtTempModel).filter_by(id=id).first()
        if not prior_art_temp_query:
            raise PriorArtTempNotFoundException('Prior art does not exist!')
        try:
            db_session.delete(prior_art_temp_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise DBException('DB error')

    @staticmethod
    def bulk_delete(prior_art_id):
        try:
            db_session.query(PriorArtTempModel).filter(
                PriorArtTempModel.prior_art_id == prior_art_id
            ).delete(synchronize_session=False)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise DBException('DB error')


def _helper_create(data):
    new_prior_art_temp = PriorArtTempModel(
        prior_art_id=data['prior_art_id'],
        prior_art_detail=data['prior_art_detail'],
        updated_at=datetime.utcnow(),
    )
    try:
        db_session.add(new_prior_art_temp)
        db_session.commit()
        prior_art_temp_query = db_session.query(
            PriorArtTempModel).get(
            new_prior_art_temp.id)
        response = schema_resource.dump(prior_art_temp_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise DBException('DB error')


def _helper_update(data, prior_art_temp_query):
    data['id'] = prior_art_temp_query.id
    data['prior_art_id'] = prior_art_temp_query.prior_art_id
    data['updated_at'] = datetime.utcnow()
    try:
        update_model(data, prior_art_temp_query)
        db_session.commit()
        response = schema_resource.dump(prior_art_temp_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise DBException('DB error')


def _build_query(params):
    q = db_session.query(
        PriorArtTempModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('prior_art_id'):
        q = q.filter_by(prior_art_id=params.get('prior_art_id'))
    return q
