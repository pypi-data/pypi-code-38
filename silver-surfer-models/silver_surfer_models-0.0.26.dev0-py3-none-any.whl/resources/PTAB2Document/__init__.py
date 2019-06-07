from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from ...database import db_session
from ...resources.PTAB2Document.models import PTAB2DocumentModel
from .schemas import (
    PTAB2DocumentResourceSchema,
    PTAB2DocumentQueryParamsSchema,
)
from ...utils.utils import update_model


schema_resource = PTAB2DocumentResourceSchema()
schema_params = PTAB2DocumentQueryParamsSchema()


class PTAB2Document(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: Dict (PTAB2DocumentResourceSchema)

        Returns:
            PTAB2DocumentResourceSchema

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
            params: PTAB2DocumentQueryParamsSchema

        Returns:
            List<PTAB2DocumentResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        ptab2_document_query = _build_query(params=data)
        response = schema_resource.dump(ptab2_document_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: PTAB2DocumentQueryParamsSchema

        Returns:
            PTAB2DocumentResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        ptab2_document_query = _build_query(params=data).one()
        response = schema_resource.dump(ptab2_document_query).data
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
        ptab2_document_query = db_session.query(
            PTAB2DocumentModel).filter_by(id=id).one()
        try:
            db_session.delete(ptab2_document_query)
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
            params: PTAB2DocumentResourceSchema

        Returns:
            PTAB2DocumentResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'document_identifier': params['document_identifier'],
            }
            ptab2_document_query = _build_query(query_params).one()
            response = _helper_update(data, ptab2_document_query)
        except NoResultFound:
            response = _helper_create(data)
        return response

    @staticmethod
    def bulk_create(mappings):
        try:
            data, errors = schema_resource.load(mappings, many=True)
            db_session.bulk_insert_mappings(
                PTAB2DocumentModel,
                data,
            )
            db_session.commit()
        except SQLAlchemyError:
            db_session.rollback()
            raise


def _helper_create(data):
    new_ptab2_document = PTAB2DocumentModel(**data)
    try:
        db_session.add(new_ptab2_document)
        db_session.commit()
        ptab2_document_query = db_session.query(
            PTAB2DocumentModel).get(new_ptab2_document.id)
        response = schema_resource.dump(ptab2_document_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, ptab2_document_query):
    data['id'] = ptab2_document_query.id
    data['document_identifier'] = ptab2_document_query.document_identifier
    try:
        update_model(data, ptab2_document_query)
        db_session.commit()
        response = schema_resource.dump(ptab2_document_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        PTAB2DocumentModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('document_identifier'):
        q = q.filter_by(document_identifier=params.get('document_identifier'))
    if params.get('proceeding_number'):
        q = q.filter_by(proceeding_number=params.get('proceeding_number'))
    return q
