from sqlalchemy.exc import SQLAlchemyError

from ...database import db_session
from ...resources.RelatedMatter.models import (
    RelatedMatterModel,
)
from .schemas import (
    RelatedMatterResourceSchema,
    RelatedMatterQueryParamsSchema,
)
from marshmallow import ValidationError


schema_resource = RelatedMatterResourceSchema()
schema_params = RelatedMatterQueryParamsSchema()


class RelatedMatter:
    @staticmethod
    def create(params):
        """
        Args:
            params: Dict (RelatedMatterResourceSchema)

        Returns:
            RelatedMatterResourceSchema

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
            params: RelatedMatterQueryParamsSchema

        Returns:
            List<RelatedMatterResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        related_matter_query = _build_query(params=data)
        response = schema_resource.dump(related_matter_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: RelatedMatterQueryParamsSchema

        Returns:
            RelatedMatterResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        related_matter_query = _build_query(params=data).one()
        response = schema_resource.dump(related_matter_query).data
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

        related_matter_query = db_session.query(
            RelatedMatterModel).filter_by(id=id).one()
        try:
            db_session.delete(related_matter_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise


def _helper_create(data):
    new_related_matter = RelatedMatterModel(**data)
    try:
        db_session.add(new_related_matter)
        db_session.commit()
        related_matter_query = db_session.query(
            RelatedMatterModel).get(
            new_related_matter.id)
        response = schema_resource.dump(related_matter_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _build_query(params):
    q = db_session.query(
        RelatedMatterModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('document_id'):
        q = q.filter_by(document_id=params.get('document_id'))
    if params.get('pacer_case_id'):
        q = q.filter_by(pacer_case_id=params.get('pacer_case_id'))
    if params.get('trial_id'):
        q = q.filter_by(trial_id=params.get('trial_id'))
    return q
