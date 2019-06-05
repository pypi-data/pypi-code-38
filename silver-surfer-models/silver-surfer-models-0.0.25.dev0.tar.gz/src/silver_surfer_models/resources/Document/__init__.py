import re

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from ...database import db_session
from ...resources.Document.models import DocumentModel
from .schemas import (
    DocumentResourceSchema,
    DocumentQueryParamsSchema,
    DocumentPatchSchema,
)
from ...utils.utils import update_model


schema_resource = DocumentResourceSchema()
schema_params = DocumentQueryParamsSchema()
schema_patch = DocumentPatchSchema()


class DBException(SQLAlchemyError):
    pass


class DocumentNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class Document:
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(DocumentResourceSchema)

        Returns: DocumentResourceSchema

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
            params: dict(DocumentQueryParamsSchema)

        Returns: List<DocumentResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        document_query = _build_query(params=data)
        response = schema_resource.dump(document_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(DocumentQueryParamsSchema)

        Returns: DocumentResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        document_query = _build_query(params=data).one()
        response = schema_resource.dump(document_query).data
        return response

    @staticmethod
    def update(id, params):
        """
        Args:
            id: int
            params: DocumentPatchSchema

        Returns: DocumentResourceSchema

        Raises:
            ValidationError
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            SQLAlchemyError
        """
        document_query = db_session.query(
            DocumentModel).filter_by(id=id).one()
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, document_query)
        return response

    @staticmethod
    def delete(id):
        """
        Args:
            id: int

        Returns: string

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            SQLAlchemyError
        """
        document_query = db_session.query(
            DocumentModel).filter_by(id=id).one()
        try:
            db_session.delete(document_query)
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
            params: DocumentResourceSchema

        Returns: DocumentResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'ptab_document_id': params['ptab_document_id'],
            }
            document_query = _build_query(query_params).one()
            response = _helper_update(data, document_query)
        except NoResultFound:
            response = _helper_create(data)
        return response

    @staticmethod
    def bulk_create(mappings):
        try:
            data, errors = schema_resource.load(mappings, many=True)
            db_session.bulk_insert_mappings(
                DocumentModel,
                data,
            )
            db_session.commit()
        except SQLAlchemyError:
            db_session.rollback()
            raise


def _helper_create(data):
    new_document = DocumentModel(**data)
    try:
        db_session.add(new_document)
        db_session.commit()
        document_query = db_session.query(
            DocumentModel).get(new_document.id)
        response = schema_resource.dump(document_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, document_query):
    data['id'] = document_query.id
    try:
        update_model(data, document_query)
        db_session.commit()
        response = schema_resource.dump(document_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        DocumentModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('trial_id'):
        q = q.filter_by(trial_id=params.get('trial_id'))
    if params.get('ptab_document_id'):
        q = q.filter_by(ptab_document_id=params.get('ptab_document_id'))
    if params.get('document_number'):
        q = q.filter_by(document_number=params.get('document_number'))
    if params.get('filing_date'):
        q = q.filter_by(filing_date=params.get('filing_date'))
    if params.get('type'):
        q = q.filter_by(type=params.get('type'))
        if params.get('type') == 'petition' and len(q.all()) > 1:
            petition_doc_ids = []
            for doc in q.all():
                if _title_contains_petition_word(doc):
                    petition_doc_ids.append(doc.id)

            if len(petition_doc_ids) > 1:
                q = q.filter_by(is_petition_doc=True)
            else:
                q = q.filter(DocumentModel.id.in_(petition_doc_ids))
    if 'file_id' in params:
        q = q.filter_by(file_id=params.get('file_id'))
    if 'has_smart_doc' in params:
        q = q.filter_by(has_smart_doc=params.get('has_smart_doc'))
    return q


def _title_contains_petition_word(document):
    match = re.search(r'petition(?:\s|$)', document.title, re.IGNORECASE)
    if document.type.lower() == 'petition' and match:
        return True
    return False
