from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from ...database import db_session
from ...resources.Company.models import (
    CompanyModel,
)
from .schemas import (
    CompanyResourceSchema,
    CompanyQueryParamsSchema,
)
from ...utils.utils import update_model


schema_resource = CompanyResourceSchema()
schema_params = CompanyQueryParamsSchema()


class Company(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(CompanyResourceSchema)

        Returns: CompanyResourceSchema

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
            params: dict(CompanyQueryParamsSchema)

        Returns: List<CompanyResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        company_query = _build_query(params=data)
        response = schema_resource.dump(
            company_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(CompanyQueryParamsSchema)

        Returns: CompanyResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        company_query = _build_query(params=data).one()
        response = schema_resource.dump(company_query).data
        return response

    @staticmethod
    def upsert(params):
        """
        Args:
            params: CompanyResourceSchema

        Returns:
            CompanyResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'applicant_full_name': params['applicant_full_name'],
            }
            company_query = _build_query(query_params).one()
            response = _helper_update(data, company_query)
        except NoResultFound:
            response = _helper_create(data)
        return response


def _helper_create(data):
    new_company = CompanyModel(**data)
    try:
        db_session.add(new_company)
        db_session.commit()
        company_query = db_session.query(CompanyModel).get(new_company.id)
        response = schema_resource.dump(company_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, company_query):
    data['id'] = company_query.id
    data['applicant_full_name'] = company_query.applicant_full_name
    try:
        update_model(data, company_query)
        db_session.commit()
        response = schema_resource.dump(company_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        CompanyModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('applicant_full_name'):
        q = q.filter_by(
            applicant_full_name=params.get('applicant_full_name'))
    if params.get('parent_company'):
        q = q.filter_by(
            parent_company=params.get('parent_company'))
    if params.get('ticker'):
        q = q.filter_by(ticker=params.get('ticker'))
    return q
