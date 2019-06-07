from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from ...database import db_session
from ...resources.CrossRef.models import CrossRefModel
from .schemas import (
    CrossRefResourceSchema,
    CrossRefQueryParamsSchema,
)
from ...utils.utils import update_model


schema_resource = CrossRefResourceSchema()
schema_params = CrossRefQueryParamsSchema()


class CrossRef:
    @staticmethod
    def create(params):
        """
        Args:
            params: Dict (CrossRefResourceSchema)

        Returns:
            CrossRefResourceSchema

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
            params: CrossRefQueryParamsSchema

        Returns:
            List<CrossRefResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        cross_ref_query = _build_query(params=data)
        response = schema_resource.dump(cross_ref_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: CrossRefQueryParamsSchema

        Returns:
            CrossRefResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        cross_ref_query = _build_query(params=data).one()
        response = schema_resource.dump(cross_ref_query).data
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
        cross_ref_query = db_session.query(
            CrossRefModel).filter_by(id=id).one()
        try:
            db_session.delete(cross_ref_query)
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
            params: CrossRefResourceSchema

        Returns:
            CrossRefResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'doi': params['doi'],
            }
            cross_ref_query = _build_query(query_params).one()
            response = _helper_update(data, cross_ref_query)
        except NoResultFound:
            response = _helper_create(data)
        return response


def _helper_create(data):
    new_cross_ref = CrossRefModel(**data)
    try:
        db_session.add(new_cross_ref)
        db_session.commit()
        cross_ref_query = db_session.query(
            CrossRefModel).get(new_cross_ref.id)
        response = schema_resource.dump(cross_ref_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, cross_ref_query):
    data['id'] = cross_ref_query.id
    data['doi'] = cross_ref_query.doi
    try:
        update_model(data, cross_ref_query)
        db_session.commit()
        response = schema_resource.dump(cross_ref_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        CrossRefModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('doi'):
        q = q.filter_by(doi=params.get('doi'))
    return q
