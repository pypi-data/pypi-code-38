from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.operators import in_op
from marshmallow import ValidationError

from ...database import db_session
from ...resources.PacerCase.models import PacerCaseModel
from .schemas import (
    PacerCaseResourceSchema,
    PacerCaseQueryParamsSchema,
    PacerCasePatchSchema,
)
from ...utils.utils import update_model


schema_resource = PacerCaseResourceSchema()
schema_params = PacerCaseQueryParamsSchema()
schema_patch = PacerCasePatchSchema()


class PacerCase:
    @staticmethod
    def create(params):
        """
        Args:
            params: Dict (PacerCaseResourceSchema)

        Returns:
            PacerCaseResourceSchema

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
            params: PacerCaseQueryParamsSchema

        Returns:
            List<PacerCaseResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        pacer_case_query = _build_query(params=data)
        response = schema_resource.dump(pacer_case_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: PacerCaseQueryParamsSchema

        Returns:
            PacerCaseResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        pacer_case_query = _build_query(params=data).one()
        response = schema_resource.dump(pacer_case_query).data
        return response

    @staticmethod
    def update(id, params):
        """

        Args:
            id: int
            params: PacerCasePatchSchema

        Returns:
            PacerCaseResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        pacer_case_query = db_session.query(
            PacerCaseModel).filter_by(id=id).one()
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, pacer_case_query)
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

        pacer_case_query = db_session.query(
            PacerCaseModel).filter_by(id=id).one()
        try:
            db_session.delete(pacer_case_query)
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
            params: PacerCaseResourceSchema

        Returns:
            PacerCaseResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'court_id': params['court_id'],
                'pacer_case_external_id': params['pacer_case_external_id'],
            }
            pacer_case_query = _build_query(query_params).one()
            response = _helper_update(data, pacer_case_query)
        except NoResultFound:
            response = _helper_create(data)
        return response


def _helper_create(data):
    new_pacer_case = PacerCaseModel(**data)
    try:
        db_session.add(new_pacer_case)
        db_session.commit()
        pacer_case_query = db_session.query(
            PacerCaseModel).get(new_pacer_case.id)
        response = schema_resource.dump(pacer_case_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, pacer_case_query):
    data['id'] = pacer_case_query.id
    data['court_id'] = pacer_case_query.court_id
    data['pacer_case_external_id'] = pacer_case_query.pacer_case_external_id
    try:
        update_model(data, pacer_case_query)
        db_session.commit()
        response = schema_resource.dump(pacer_case_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        PacerCaseModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if 'ids' in params:
        q = q.filter(in_op(
            PacerCaseModel.id,
            params['ids'],
        ))
    if params.get('case_no'):
        q = q.filter_by(case_no=params.get('case_no'))
    if params.get('court_id'):
        q = q.filter_by(court_id=params.get('court_id'))
    if params.get('pacer_case_external_id'):
        q = q.filter_by(
            pacer_case_external_id=params.get('pacer_case_external_id'))
    return q
