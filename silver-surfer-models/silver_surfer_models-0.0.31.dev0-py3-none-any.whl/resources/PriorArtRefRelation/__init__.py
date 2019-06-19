from sqlalchemy.exc import SQLAlchemyError

from ...database import db_session
from ...resources.PriorArtRefRelation.models import (
    PriorArtRefRelationModel,
)
from .schemas import (
    PriorArtRefRelationResourceSchema,
    PriorArtRefRelationQueryParamsSchema,
)
from marshmallow import ValidationError


schema_resource = PriorArtRefRelationResourceSchema()
schema_params = PriorArtRefRelationQueryParamsSchema()


class PriorArtRefRelation:
    @staticmethod
    def create(params):
        """
        Args:
            params: Dict (PriorArtRefRelationResourceSchema)

        Returns:
            PriorArtRefRelationResourceSchema

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
            params: PriorArtRefRelationQueryParamsSchema

        Returns:
            List<PriorArtRefRelationResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        pa_ref_relation_query = _build_query(params=data)
        response = schema_resource.dump(pa_ref_relation_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: PriorArtRefRelationQueryParamsSchema

        Returns:
            PriorArtRefRelationResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        pa_ref_relation_query = _build_query(params=data).one()
        response = schema_resource.dump(pa_ref_relation_query).data
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

        pa_ref_relation_query = db_session.query(
            PriorArtRefRelationModel).filter_by(
            id=id).one()
        try:
            db_session.delete(pa_ref_relation_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise


def _helper_create(data):
    new_pa_ref_relation = PriorArtRefRelationModel(**data)
    try:
        db_session.add(new_pa_ref_relation)
        db_session.commit()
        pa_ref_relation_query = db_session.query(
            PriorArtRefRelationModel).get(
            new_pa_ref_relation.id)
        response = schema_resource.dump(pa_ref_relation_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _build_query(params):
    q = db_session.query(
        PriorArtRefRelationModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('prior_art_id'):
        q = q.filter_by(prior_art_id=params.get('prior_art_id'))
    if params.get('cross_ref_id'):
        q = q.filter_by(cross_ref_id=params.get('cross_ref_id'))
    if params.get('patent_id'):
        q = q.filter_by(patent_id=params.get('patent_id'))
    if params.get('patent_application_id'):
        q = q.filter_by(
            patent_application_id=params.get('patent_application_id'))
    return q
