from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from marshmallow import ValidationError

from ...database import db_session
from ...utils.utils import update_model
from .models import (
    AbstractTextModel,
)
from .schemas import (
    AbstractTextResourceSchema,
    AbstractTextQueryParamsSchema,
    AbstractTextPatchSchema,
)


schema_resource = AbstractTextResourceSchema()
schema_params = AbstractTextQueryParamsSchema()
schema_patch = AbstractTextPatchSchema()


class DBException(SQLAlchemyError):
    pass


class AbstractTextNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class AbstractText:
    @staticmethod
    def create(params):
        """
        :param
            Dict
                patent_id: int
                abstract_text: string
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
        abstract_text_query = _build_query(params=data)
        response = schema_resource.dump(abstract_text_query, many=True).data
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
        abstract_text_query = _build_query(params=data).one()
        response = schema_resource.dump(abstract_text_query).data
        return response

    @staticmethod
    def update(id, params):
        """
        :param
            id: integer: required
            params: dict
                abstract_text
        :return:
            newly updated object
        :exception:
            AbstractTextNotFoundException
            ValidationError
            DBException
        """
        abstract_text_query = db_session.query(
            AbstractTextModel).filter_by(id=id).first()
        if not abstract_text_query:
            raise AbstractTextNotFoundException('Abstract not found!')
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, abstract_text_query)
        return response

    @staticmethod
    def delete(id):
        """
        :param
            id
        :return:
            delete message
        :exception:
            AbstractTextNotFoundException
            DBException
        """

        abstract_text_query = db_session.query(
            AbstractTextModel).filter_by(id=id).first()
        if not abstract_text_query:
            raise AbstractTextNotFoundException('Abstract does not exist!')
        try:
            db_session.delete(abstract_text_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise DBException('DB error')


def _helper_create(data):
    new_abstract_text = AbstractTextModel(
        patent_id=data['patent_id'],
        abstract_text=data['abstract_text'],
        updated_at=datetime.utcnow(),
    )
    try:
        db_session.add(new_abstract_text)
        db_session.commit()
        abstract_text_query = db_session.query(
            AbstractTextModel).get(new_abstract_text.id)
        response = schema_resource.dump(abstract_text_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, abstract_text_query):
    data['id'] = abstract_text_query.id
    data['patent_id'] = abstract_text_query.patent_id
    data['updated_at'] = datetime.utcnow()
    try:
        update_model(data, abstract_text_query)
        db_session.commit()
        response = schema_resource.dump(abstract_text_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise DBException('DB error')


def _build_query(params):

    q = db_session.query(AbstractTextModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('patent_id'):
        q = q.filter_by(patent_id=params.get('patent_id'))
    return q
