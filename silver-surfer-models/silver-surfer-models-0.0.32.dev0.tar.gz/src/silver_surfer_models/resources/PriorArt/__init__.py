from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from marshmallow import ValidationError

from ...database import db_session
from ...utils.utils import update_model
from ...resources.PriorArt.models import PriorArtModel
from .schemas import (
    PriorArtResourceSchema,
    PriorArtQueryParamsSchema,
    PriorArtPatchSchema,
)


schema_resource = PriorArtResourceSchema()
schema_params = PriorArtQueryParamsSchema()
schema_patch = PriorArtPatchSchema()


class PriorArtDBException(SQLAlchemyError):
    pass


class PriorArtNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class PriorArt:
    @staticmethod
    def create(params):
        """
        :param
            PriorArtResourceSchema
        :return:
            PriorArtResourceSchema
        :exception:
            ValidationError
            PriorArtDBException
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
            PriorArtQueryParamsSchema
        :return:
            queried object
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        prior_art_query = _build_query(params=data)
        response = schema_resource.dump(prior_art_query, many=True).data
        return response

    @staticmethod
    def update(id, params):
        """
        :param
            id: integer: required
            params: dict
                prior_art
                prior_art_detail
        :return:
            PriorArtResourceSchema
        :exception:
            PriorArtNotFoundException
            ValidationError
            PriorArtDBException
        """
        prior_art_query = db_session.query(
            PriorArtModel).filter_by(id=id).first()
        if not prior_art_query:
            raise PriorArtNotFoundException('Prior art not found!')
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, prior_art_query)
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
            PriorArtDBException
        """

        prior_art_query = db_session.query(
            PriorArtModel).filter_by(id=id).first()
        if not prior_art_query:
            raise PriorArtNotFoundException('Prior art does not exist!')
        try:
            db_session.delete(prior_art_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise PriorArtDBException('DB error')

    def upsert(self, params):
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        prior_art_query = db_session.query(
            PriorArtModel).filter_by(
            document_id=params['document_id'],
            tag=params['tag'],
        ).first()

        if not prior_art_query:
            response = _helper_create(data)
        else:
            response = _helper_update(data, prior_art_query)
        return response

    @staticmethod
    def bulk_delete(document_id):
        try:
            db_session.query(PriorArtModel).filter(
                PriorArtModel.document_id == document_id
            ).delete(synchronize_session=False)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise

    def bulk_update(self, document_id, patch_data):
        prior_arts = self.read({'document_id': document_id})
        allowed_prior_art_ids = [pa['id'] for pa in prior_arts]
        update_data = {}
        for prior_art_id in patch_data:
            if int(prior_art_id) in allowed_prior_art_ids:
                update_data[int(prior_art_id)] = patch_data[prior_art_id]

        for prior_art_id in update_data:
            self.update(
                id=prior_art_id,
                params={'prior_art_detail': update_data[prior_art_id]},
            )
        return self.read({'document_id': document_id})


def _helper_create(data):
    new_prior_art = PriorArtModel(
        document_id=data['document_id'],
        tag=data['tag'],
        title=data['title'],
        exhibit=data['exhibit'],
        updated_at=datetime.utcnow(),
    )
    try:
        db_session.add(new_prior_art)
        db_session.commit()
        prior_art_query = db_session.query(
            PriorArtModel).get(new_prior_art.id)
        response = schema_resource.dump(prior_art_query).data
        db_session.close()
        return response
    except SQLAlchemyError as e:
        db_session.rollback()
        db_session.close()
        raise PriorArtDBException('DB error {}'.format(str(e)))


def _helper_update(data, prior_art_query):
    data['id'] = prior_art_query.id
    data['document_id'] = prior_art_query.document_id
    data['tag'] = prior_art_query.tag
    data['updated_at'] = datetime.utcnow()
    try:
        update_model(data, prior_art_query)
        db_session.commit()
        response = schema_resource.dump(prior_art_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise PriorArtDBException('DB error')


def _build_query(params):
    q = db_session.query(
        PriorArtModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('document_id'):
        q = q.filter_by(document_id=params.get('document_id'))
    if params.get('tag'):
        q = q.filter_by(tag=params.get('tag'))
    return q
