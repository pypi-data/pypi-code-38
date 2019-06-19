from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime

from anji_orm import (
    ensure_element, QueryTable, QueryAst, Model
)
from sanic.request import Request
from sanic.response import json
from sanic_openapi import doc

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['DataTableMixin', 'OpenAPIDescriptionMixin', 'web_filter_doc', 'SEARCH_TARGET_FIELD_MARK']


SEARCH_TARGET_FIELD_MARK = 'search_target'


def web_filter_doc(func):
    return doc.consumes(
        {"filter": doc.String("Filter for match expression")},
        {"pageIndex": doc.String("Index of current page")},
        {"sortDirection": doc.String("Direction for sorting", choices=('desc', 'asc'))},
        {"pageSize": doc.Integer("Size for page")},
        {"sortColumn": doc.String("Column for sorting")}
    )(func)


class DataTableMixin(Model):

    async def convert_to_web_info(self) -> Dict[str, Any]:
        fields = {}
        for field_name, field_item in self._fields.items():
            if not field_item.internal and getattr(self, field_name) is not None:
                fields[field_item.name] = await field_item.async_format(getattr(self, field_name))
        return fields

    async def convert_to_json_data(self) -> Dict[str, Any]:
        fields = {}
        for field_name, field_item in self._fields.items():
            if not field_item.internal and getattr(self, field_name) is not None:
                fields[field_item.name] = await ensure_element(getattr(self, field_name))
        fields['id'] = self.id
        return fields

    @classmethod
    def process_before_filter(cls, db_request: QueryAst, _request: Request) -> QueryAst:
        return db_request

    @classmethod
    def process_after_filter(cls, db_request: QueryAst, _request: Request) -> QueryAst:
        return db_request

    @classmethod
    def process_filter(cls, db_request: QueryAst, search_field: Optional[str], request: Request) -> QueryAst:
        if 'filter' in request.args and search_field is not None:
            if isinstance(db_request, QueryTable):
                return getattr(cls, search_field).match(request.args.get('filter'))
            return db_request & getattr(cls, search_field).match(request.args.get('filter'))
        return db_request

    @classmethod
    def process_sort(cls, db_request: QueryAst, request: Request) -> QueryAst:
        column_link = getattr(cls, request.args.get('sortColumn')).amount
        if request.args.get('sortDirection') == 'desc':
            column_link = column_link.desc
        return db_request.order_by(column_link)

    @classmethod
    def process_pager(cls, db_request: QueryAst, request: Request) -> QueryAst:
        page_index = int(request.args.get('pageIndex'))
        page_size = int(request.args.get('pageSize'))
        return db_request.skip(page_index * page_size).limit(page_size)

    @classmethod
    async def process_web_request(cls, request: Request, prettify_response: bool = True) -> Dict[str, Any]:
        search_field = cls._field_marks.get(SEARCH_TARGET_FIELD_MARK, None)
        db_request: QueryTable = cls.all()
        db_request = cls.process_before_filter(db_request, request)
        db_request = cls.process_filter(db_request, search_field, request)
        db_request = cls.process_after_filter(db_request, request)
        total_count = await db_request.count().async_run()
        if 'sortColumn' in request.args:
            db_request = cls.process_sort(db_request, request)
        if 'pageIndex' in request.args and 'pageSize' in request.args:
            db_request = cls.process_pager(db_request, request)
        records = await db_request.async_run()
        if prettify_response:
            return json(
                {
                    'data': [await record.convert_to_web_info() for record in records],
                    'total': total_count
                }
            )
        return json(
            {
                'data': [await record.convert_to_json_data() for record in records],
                'total': total_count
            }
        )


class OpenAPIDescriptionMixin(Model):

    _doc_field_mapping = {
        str: doc.String,
        Enum: doc.String,
        datetime: doc.DateTime,
        bool: doc.Boolean,
        int: doc.Integer,
        float: doc.Float,
        Dict: doc.Dictionary,
        List: doc.List,
    }

    @classmethod
    def map_field(cls, field):
        if field.param_type in cls._doc_field_mapping:
            doc_class = cls._doc_field_mapping[field.param_type]
            return doc_class(description=field.description)
        return doc.String(field.description)

    @classmethod
    def get_full_description(cls):
        if not hasattr(cls, '__openapi_full_description__'):
            cls.__openapi_full_description__ = type(cls.__name__, (), {
                field_name: OpenAPIDescriptionMixin.map_field(field)
                for field_name, field in cls._fields.items()
            })
        return cls.__openapi_full_description__

    @classmethod
    def get_create_description(cls):
        return cls.get_description(ignore_list=('id', 'orm_last_write_timestamp'))

    @classmethod
    def get_description(cls, ignore_list=tuple()):
        if not hasattr(cls, '__openapi_create_description__'):
            cls.__openapi_create_description__ = type(cls.__name__ + 'Data', (), {
                field_name: OpenAPIDescriptionMixin.map_field(field)
                for field_name, field in cls._fields.items() if not field.internal and field_name not in ignore_list
            })
        return cls.__openapi_create_description__
