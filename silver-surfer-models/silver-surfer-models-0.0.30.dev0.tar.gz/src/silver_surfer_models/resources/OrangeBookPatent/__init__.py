from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.operators import in_op
from datetime import datetime
from marshmallow import ValidationError

from ...database import db_session
from ...utils.utils import update_model
from ...resources.OrangeBookPatent.models import (
    OrangeBookPatentModel,
)
from .schemas import (
    OrangeBookPatentResourceSchema,
    OrangeBookPatentQueryParamsSchema,
    OrangeBookPatentPatchSchema,
)


schema_resource = OrangeBookPatentResourceSchema()
schema_params = OrangeBookPatentQueryParamsSchema()
schema_patch = OrangeBookPatentPatchSchema()


class DBException(SQLAlchemyError):
    pass


class OrangeBookPatentNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class OrangeBookPatent:
    @staticmethod
    def create(params):
        """
        :param
            Dict: OrangeBookPatentResourceSchema
        :return:
            OrangeBookPatentResourceSchema
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
            params: OrangeBookPatentQueryParamsSchema
        :return:
            List<OrangeBookPatentResourceSchema>
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        orange_book_patent_query = _build_query(params=data)
        response = schema_resource.dump(
            orange_book_patent_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        :param
            params: OrangeBookPatentQueryParamsSchema
        :return:
            OrangeBookPatentResourceSchema
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        orange_book_patent_query = _build_query(params=data).one()
        response = schema_resource.dump(orange_book_patent_query).data
        return response

    @staticmethod
    def update(id, params):
        """
        :param
            id: integer: required
            params: OrangeBookPatentPatchSchema
        :return:
            OrangeBookPatentResourceSchema
        :exception:
            OrangeBookPatentNotFoundException
            ValidationError
            DBException
        """
        orange_book_patent_query = db_session.query(
            OrangeBookPatentModel).filter_by(
            id=id,
        ).first()
        if not orange_book_patent_query:
            raise OrangeBookPatentNotFoundException('OB Patent not found!')
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, orange_book_patent_query)
        return response

    @staticmethod
    def upsert(params):
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        orange_book_patent_query = db_session.query(
            OrangeBookPatentModel).filter_by(
            patent_no=params.get('patent_no'),
            product_no=params.get('product_no'),
        ).first()

        if not orange_book_patent_query:
            response = _helper_create(data)
        else:
            response = _helper_update(data, orange_book_patent_query)
        return response


def _helper_create(data):
    new_orange_book_patent = OrangeBookPatentModel(
        updated_at=datetime.utcnow(),
        **data,
    )
    try:
        db_session.add(new_orange_book_patent)
        db_session.commit()
        orange_book_patent_query = db_session.query(
            OrangeBookPatentModel).get(
            new_orange_book_patent.id,
        )
        response = schema_resource.dump(orange_book_patent_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, orange_book_patent_query):
    data['id'] = orange_book_patent_query.id
    data['product_no'] = orange_book_patent_query.product_no
    data['patent_no'] = orange_book_patent_query.patent_no
    data['updated_at'] = datetime.utcnow()
    try:
        update_model(data, orange_book_patent_query)
        db_session.commit()
        response = schema_resource.dump(orange_book_patent_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        OrangeBookPatentModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('appl_no'):
        q = q.filter_by(appl_no=params.get('appl_no'))
    if 'appl_nos' in params:
        q = q.filter(in_op(
            OrangeBookPatentModel.appl_no,
            params.get('appl_nos'),
        ))
    if params.get('product_no'):
        q = q.filter_by(product_no=params.get('product_no'))
    if params.get('patent_no'):
        q = q.filter_by(patent_no=params.get('patent_no'))
    return q
