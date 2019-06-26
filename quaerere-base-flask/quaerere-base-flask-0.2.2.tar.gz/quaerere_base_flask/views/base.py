__all__ = ['BaseView']

import logging

from arango.exceptions import (
    ArangoServerError,
    AQLQueryExecuteError,
    DocumentInsertError)
from arango_orm.exceptions import DocumentNotFoundError
from flask import jsonify, request
from flask_classful import FlaskView

from quaerere_base_flask.schemas import (
    ArangoDBFilterSchema,
    ArangoDBMetadataSchema)

LOGGER = logging.getLogger(__name__)


class BaseView(FlaskView):
    """Base class for defining a Restful access method to a resource

    BaseView provides basic Restful access to a resource defined by a given
    data object and schema.

    Current supported functionality
     * :py:meth:`index`
     * :py:meth:`get`
     * :py:meth:`post`
    """

    def __init__(self, model, schema, get_db):
        """

        :param model: Model class for data encapsulation
        :param schema: Schema class for data validation
        :param get_db: Function reference for acquiring a DB connection
        """
        self._obj_model = model
        self._obj_schema = schema
        self._get_db = get_db

    def index(self):
        """Returns all objects

        :returns: All objects of the model type
        """
        db_conn = self._get_db()
        db_result = db_conn.query(self._obj_model).all()
        resp_schema = self._obj_schema(many=True)
        return jsonify(resp_schema.dump(db_result).data)

    def get(self, key):
        """Get a specific object by key

        :param key: Primary key of an object to retrieve
        :returns: Object of provided key
        """
        db_conn = self._get_db()
        try:
            db_result = db_conn.query(self._obj_model).by_key(key)
        except DocumentNotFoundError as err:
            return jsonify({'errors': err.message}), 404
        resp_schema = self._obj_schema()
        return jsonify(resp_schema.dump(db_result).data)

    def post(self):
        """Create a new object

        :returns: DB Insert metadata
        """
        db_conn = self._get_db()
        if request.data:
            LOGGER.debug(f'Received POST data', extra={'data': request.data})
        else:
            msg = {'errors': 'No data received'}
            return jsonify(msg), 400
        req_schema = self._obj_schema()
        resp_schema = ArangoDBMetadataSchema()
        unmarshal = req_schema.load(request.get_json())
        if len(unmarshal.errors) != 0:
            return jsonify({'errors': unmarshal.errors}), 400
        try:
            result = db_conn.add(unmarshal.data)
            return jsonify(resp_schema.dump(result).data), 201
        except DocumentInsertError as e:
            return jsonify({'errors': e.error_message}), e.http_code

    def put(self, key):
        """Update all fields on an object

        :param key: Key of object
        :returns: DB Update metadata
        """
        db_conn = self._get_db()
        if request.data:
            LOGGER.debug(f'Received POST data', extra={'data': request.data})
        else:
            msg = {'errors': 'No data received'}
            return jsonify(msg), 400
        data = request.get_json()
        if '_key' not in data:
            data['_key'] = key
        req_schema = self._obj_schema()
        resp_schema = ArangoDBMetadataSchema()
        unmarshal = req_schema.load(data)
        if len(unmarshal.errors) != 0:
            return jsonify({'errors': unmarshal.errors}), 400
        try:
            result = db_conn.update(unmarshal.data)
            return jsonify(resp_schema.dump(result).data), 201
        except ArangoServerError as e:
            return jsonify({'errors': e.error_message}), e.http_code

    def patch(self, key):
        """Update specific data elements

        :param key: Key of object
        :return: DB Update metadata
        """
        db_conn = self._get_db()
        if request.data:
            LOGGER.debug(f'Received POST data', extra={'data': request.data})
        else:
            msg = {'errors': 'No data received'}
            return jsonify(msg), 400
        data = request.get_json()
        if '_key' not in data:
            data['_key'] = key
        elements = data.keys()
        req_schema = self._obj_schema(only=elements)
        resp_schema = ArangoDBMetadataSchema()
        unmarshal = req_schema.load(data)
        if len(unmarshal.errors) != 0:
            return jsonify({'errors': unmarshal.errors}), 400
        try:
            result = db_conn.update(unmarshal.data)
            return jsonify(resp_schema.dump(result).data), 201
        except ArangoServerError as e:
            return jsonify({'errors': e.error_message}), e.http_code

    def delete(self, key):
        """Delete an object

        :param key: Key of object
        :return: DB Delete metadata
        """
        db_conn = self._get_db()
        resp_schema = ArangoDBMetadataSchema()
        try:
            ent = db_conn.query(self._obj_model).by_key(key)
            result = db_conn.delete(ent)
            return jsonify(resp_schema.dump(result).data), 202
        except ArangoServerError as e:
            return jsonify({'errors': e.error_message}), e.http_code

    def find(self):
        """Find an object based on criteria

        :return: objects
        """
        LOGGER.debug(request.args)
        req_schema = ArangoDBFilterSchema()
        req_args = req_schema.load(request.args)
        if len(req_args.errors) != 0:
            return jsonify({'errors': req_args.errors}), 400
        find_query = req_args.data
        db_conn = self._get_db()
        sort = None
        limit = None
        if 'sort' in find_query:
            sort = find_query['sort']
        if 'limit' in find_query:
            limit = find_query['limit']
        variables = find_query['variables']
        _or = find_query['_or']
        try:
            result = db_conn.query(self._obj_model)
            for condition in find_query['conditions']:
                result = result.filter(condition, _or=_or, **variables)
            if sort is not None:
                result = result.sort(sort)
            if limit is not None:
                result = result.limit(limit)
            obj_schema = self._obj_schema(many=True)
            msg = {'query': find_query,
                   'result': obj_schema.dump(result.all()).data}
        except AQLQueryExecuteError as e:
            return jsonify(
                {'query': find_query,
                 'errors': e.error_message}), e.http_code
        return jsonify(msg), 200
