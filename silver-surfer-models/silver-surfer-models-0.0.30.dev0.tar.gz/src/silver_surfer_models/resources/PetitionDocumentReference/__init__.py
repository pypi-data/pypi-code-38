import re

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from ...database import db_session
from ...resources.PetitionDocumentReference.models import (
    PetitionDocumentReferenceModel,
)
from .schemas import (
    PetitionDocumentReferenceResourceSchema,
    PetitionDocumentReferenceQueryParamsSchema,
)


schema_resource = PetitionDocumentReferenceResourceSchema()
schema_params = PetitionDocumentReferenceQueryParamsSchema()


class PetitionDocumentReference(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(PetitionDocumentReferenceResourceSchema)

        Returns: PetitionDocumentReferenceResourceSchema

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
            params: dict(PetitionDocumentReferenceQueryParamsSchema)

        Returns: List<PetitionDocumentReferenceResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        petition_document_ref_query = _build_query(params=data)
        response = schema_resource.dump(
            petition_document_ref_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(PetitionDocumentReferenceQueryParamsSchema)

        Returns: PetitionDocumentReferenceResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        petition_document_ref_query = _build_query(params=data).one()
        response = schema_resource.dump(petition_document_ref_query).data
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
        petition_document_ref_query = db_session.query(
            PetitionDocumentReferenceModel).filter_by(id=id).one()
        try:
            db_session.delete(petition_document_ref_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise

    @staticmethod
    def bulk_delete(document_id):
        try:
            db_session.query(
                PetitionDocumentReferenceModel).filter(
                PetitionDocumentReferenceModel.document_id == document_id
            ).delete(synchronize_session=False)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise


def _helper_create(data):
    new_petition_document_reference = PetitionDocumentReferenceModel(**data)
    try:
        db_session.add(new_petition_document_reference)
        db_session.commit()
        petition_document_ref_query = db_session.query(
            PetitionDocumentReferenceModel).get(
            new_petition_document_reference.id)
        response = schema_resource.dump(petition_document_ref_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _build_query(params):
    q = db_session.query(
        PetitionDocumentReferenceModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('document_id'):
        q = q.filter_by(document_id=params.get('document_id'))
    if params.get('type'):
        q = q.filter_by(type=params.get('type'))
    if params.get('value'):
        q = q.filter_by(value=params.get('value'))
    return q


def _is_petition_doc(document):
    match = re.search(r'petition(?:\s|$)', document.title, re.IGNORECASE)
    if document.type == 'petition' and match:
        return True
    return False
