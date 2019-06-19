from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from marshmallow import ValidationError

from ...database import db_session
from ...utils.utils import update_model
from ...resources.OrangeBookProduct.models import (
    OrangeBookProductModel,
)
from .schemas import (
    OrangeBookProductResourceSchema,
    OrangeBookProductQueryParamsSchema,
    OrangeBookProductPatchSchema,
)


schema_resource = OrangeBookProductResourceSchema()
schema_params = OrangeBookProductQueryParamsSchema()
schema_patch = OrangeBookProductPatchSchema()


class DBException(SQLAlchemyError):
    pass


class OrangeBookProductNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class OrangeBookProduct:
    @staticmethod
    def create(params):
        """
        :param
            Dict: OrangeBookProductResourceSchema
        :return:
            OrangeBookProductResourceSchema
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
            params: OrangeBookProductQueryParamsSchema
        :return:
            List<OrangeBookProductResourceSchema>
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        orange_book_product_query = _build_query(params=data)
        response = schema_resource.dump(
            orange_book_product_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        :param
            params: OrangeBookProductQueryParamsSchema
        :return:
            OrangeBookProductResourceSchema
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        orange_book_product_query = _build_query(params=data).one()
        response = schema_resource.dump(orange_book_product_query).data
        return response

    @staticmethod
    def update(id, params):
        """
        :param
            id: integer: required
            params: OrangeBookProductPatchSchema
        :return:
            OrangeBookProductResourceSchema
        :exception:
            OrangeBookProductNotFoundException
            ValidationError
            DBException
        """
        orange_book_product_query = db_session.query(
            OrangeBookProductModel).filter_by(
            id=id,
        ).first()
        if not orange_book_product_query:
            raise OrangeBookProductNotFoundException('OB Product not found!')
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, orange_book_product_query)
        return response

    @staticmethod
    def upsert(params):
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        orange_book_product_query = db_session.query(
            OrangeBookProductModel).filter_by(
            appl_no=params['appl_no'],
            product_no=params['product_no'],
        ).first()

        if not orange_book_product_query:
            response = _helper_create(data)
        else:
            response = _helper_update(data, orange_book_product_query)
        return response


def _helper_create(data):
    new_orange_book_product = OrangeBookProductModel(
        updated_at=datetime.utcnow(),
        **data,
    )
    try:
        db_session.add(new_orange_book_product)
        db_session.commit()
        orange_book_product_query = db_session.query(
            OrangeBookProductModel).get(
            new_orange_book_product.id,
        )
        response = schema_resource.dump(orange_book_product_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, orange_book_product_query):
    data['id'] = orange_book_product_query.id
    data['appl_no'] = orange_book_product_query.appl_no
    data['product_no'] = orange_book_product_query.product_no
    data['updated_at'] = datetime.utcnow()
    try:
        update_model(data, orange_book_product_query)
        db_session.commit()
        response = schema_resource.dump(orange_book_product_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        OrangeBookProductModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('appl_no'):
        q = q.filter_by(appl_no=params.get('appl_no'))
    if params.get('product_no'):
        q = q.filter_by(product_no=params.get('product_no'))
    if params.get('trade_name'):
        q = q.filter(OrangeBookProductModel.trade_name.op('regexp')(
            params.get('trade_name')))
    return q
