import json
from base64 import b64encode

from flask import request, session, Response
from munch import munchify
from probator.config import DBCChoice, DBCString, DBCInt, DBCFloat, DBCArray, DBCJSON, DBCText, apply_config
from probator.constants import ROLE_ADMIN, HTTP
from probator.database import db
from probator.json_utils import ProbatorJSONEncoder, ProbatorJSONDecoder
from probator.log import auditlog
from probator.plugins import BaseView
from probator.schema import ConfigNamespace, ConfigItem
from probator.wrappers import check_auth, rollback


def _to_dbc_class(args):
    if args.type == 'choice':
        if type(args.value) == str:
            return DBCChoice(json.loads(args.value))

        return DBCChoice(args.value)

    elif args.type == 'string':
        return DBCString(args.value)

    elif args.type == 'int':
        return DBCInt(args.value)

    elif args.type == 'float':
        return DBCFloat(args.value)

    elif args.type == 'array':
        return DBCArray(args.value)

    elif args.type == 'json':
        return DBCJSON(json.loads(args.value))

    elif args.type == 'text':
        return DBCText(args.value)

    elif args.type == 'bool':
        if isinstance(args.value, bool):
            return args.value

        return True if args.value.lower() == 'true' else False

    else:
        raise ValueError(f'Invalid config type: {args.type}')


class ConfigList(BaseView):
    URLS = ['/api/v1/config']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self):
        """List existing config namespaces and their items"""
        namespaces = db.ConfigNamespace.order_by(
            ConfigNamespace.sort_order,
            ConfigNamespace.name
        ).all()

        return self.make_response({
            'message': None,
            'namespaces': namespaces
        }, HTTP.OK)

    @rollback
    @check_auth(ROLE_ADMIN)
    def post(self):
        """Create a new config item"""
        args = munchify(request.json)

        if not self.dbconfig.namespace_exists(args.namespacePrefix):
            return self.make_response('The namespace doesnt exist', HTTP.NOT_FOUND)

        if self.dbconfig.key_exists(args.namespacePrefix, args.key):
            return self.make_response('This config item already exists', HTTP.CONFLICT)

        self.dbconfig.set(args.namespacePrefix, args.key, _to_dbc_class(args), description=args.description)
        auditlog(event='configItem.create', actor=session['user'].username, data=args)

        return self.make_response('Config item added', HTTP.CREATED)


class ConfigGet(BaseView):
    URLS = ['/api/v1/config/<string:namespace>/<string:key>']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self, namespace, key):
        """Get a specific configuration item"""
        cfg = self.dbconfig.get(key, namespace, as_object=True)
        return self.make_response({
            'message': None,
            'config': cfg
        })

    @rollback
    @check_auth(ROLE_ADMIN)
    def put(self, namespace, key):
        """Update a single configuration item"""
        args = munchify(request.json)

        if not self.dbconfig.key_exists(namespace, key):
            return self.make_response(f'No such config entry: {namespace}/{key}', HTTP.BAD_REQUEST)

        if args.type == 'choice':
            enabled_count = len(args.value.enabled)
            if enabled_count < args.value.min_items:
                return self.make_response(f'You need to select at least {args.value.min_items} items', HTTP.BAD_REQUEST)

            if enabled_count > args.value.max_items:
                return self.make_response(f'You can select at most {args.value.max_items} items', HTTP.BAD_REQUEST)

        if args.type == 'choice' and not set(args.value.enabled).issubset(args.value.available):
            return self.make_response('Invalid item', HTTP.BAD_REQUEST)

        item = db.ConfigItem.find_one(
            ConfigItem.namespace_prefix == namespace, ConfigItem.key == key
        )

        if item.value != args.value:
            item.value = args.value

        if item.type != args.type:
            item.type = args.type

        if item.description != args.description:
            item.description = args.description

        self.dbconfig.set(namespace, key, _to_dbc_class(args))
        auditlog(event='configItem.update', actor=session['user'].username, data=args)

        return self.make_response('Config entry updated')

    @rollback
    @check_auth(ROLE_ADMIN)
    def delete(self, namespace, key):
        """Delete a specific configuration item"""
        if not self.dbconfig.key_exists(namespace, key):
            return self.make_response(f'No such config entry exists: {namespace}/{key}', HTTP.BAD_REQUEST)

        self.dbconfig.delete(namespace, key)
        auditlog(event='configItem.delete', actor=session['user'].username, data={'namespace': namespace, 'key': key})
        return self.make_response('Config entry deleted')


class NamespaceGet(BaseView):
    URLS = ['/api/v1/namespace/<string:namespace_prefix>']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self, namespace_prefix):
        """Get a specific configuration namespace"""
        ns = db.ConfigNamespace.find_one(ConfigNamespace.namespace_prefix == namespace_prefix)
        if not ns:
            return self.make_response(f'No such namespace: {namespace_prefix}', HTTP.NOT_FOUND)

        return self.make_response({'namespace': ns})

    @rollback
    @check_auth(ROLE_ADMIN)
    def put(self, namespace_prefix):
        """Update a specific configuration namespace"""
        self.reqparse.add_argument('name', type=str, required=True)
        self.reqparse.add_argument('sortOrder', type=int, required=True)
        args = self.reqparse.parse_args()

        ns = db.ConfigNamespace.find_one(ConfigNamespace.namespace_prefix == namespace_prefix)
        if not ns:
            return self.make_response(f'No such namespace: {namespace_prefix}', HTTP.NOT_FOUND)

        ns.name = args.name
        ns.sort_order = args.sortOrder
        db.session.add(ns)
        db.session.commit()

        self.dbconfig.reload_data()
        auditlog(event='configNamespace.update', actor=session['user'].username, data=args)

        return self.make_response('Namespace updated')

    @rollback
    @check_auth(ROLE_ADMIN)
    def delete(self, namespace_prefix):
        """Delete a specific configuration namespace"""
        ns = db.ConfigNamespace.find_one(ConfigNamespace.namespace_prefix == namespace_prefix)
        if not ns:
            return self.make_response(f'No such namespace: {namespace_prefix}', HTTP.NOT_FOUND)

        db.session.delete(ns)
        db.session.commit()

        self.dbconfig.reload_data()
        auditlog(
            event='configNamespace.delete',
            actor=session['user'].username,
            data={'namespacePrefix': namespace_prefix}
        )
        return self.make_response('Namespace deleted')


class Namespaces(BaseView):
    URLS = ['/api/v1/namespace']

    @rollback
    @check_auth(ROLE_ADMIN)
    def post(self):
        """Create a new configuration namespace"""
        self.reqparse.add_argument('namespacePrefix', type=str, required=True)
        self.reqparse.add_argument('name', type=str, required=True)
        self.reqparse.add_argument('sortOrder', type=int, required=True)
        args = self.reqparse.parse_args()

        if self.dbconfig.namespace_exists(args.namespacePrefix):
            return self.make_response(f'Namespace {args.namespacePrefix} already exists', HTTP.CONFLICT)

        ns = ConfigNamespace()

        ns.namespace_prefix = args.namespacePrefix
        ns.name = args.name
        ns.sort_order = args.sortOrder

        db.session.add(ns)
        db.session.commit()

        self.dbconfig.reload_data()
        auditlog(event='configNamespace.create', actor=session['user'].username, data=args)

        return self.make_response('Namespace created', HTTP.CREATED)


class ConfigImportExport(BaseView):
    URLS = ['/api/v1/config/imex']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self):
        out = [ns.to_json() for ns in db.ConfigNamespace.find()]

        auditlog(event='config.export', actor=session['user'].username, data={})
        return Response(
            response=b64encode(
                bytes(
                    json.dumps(out, cls=ProbatorJSONEncoder),
                    'utf-8'
                )
            ),
            status=HTTP.OK
        )

    @rollback
    @check_auth(ROLE_ADMIN)
    def post(self):
        self.reqparse.add_argument('config', type=str, required=True)
        args = self.reqparse.parse_args()

        try:
            config = json.loads(args.config, cls=ProbatorJSONDecoder)
            apply_config(config)
            auditlog(event='config.import', actor=session['user'].username, data=config)
            return self.make_response('Configuration imported')

        except Exception as ex:
            self.log.exception('Failed importing configuration data')
            return self.make_response(f'Error importing configuration data: {ex}', HTTP.SERVER_ERROR)
