import re
import shlex

from flask import session, current_app
from flask_restful import inputs
from probator.constants import ROLE_USER, RGX_TAG, RGX_PROPERTY, HTTP
from probator.database import db
from probator.plugins import BaseView
from probator.plugins.types.resources import BaseResource
from probator.schema import Resource, ResourceType, Tag, Account, ResourceProperty
from probator.utils import from_camelcase, is_truthy
from probator.wrappers import check_auth, rollback
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import aliased


class ResourceGet(BaseView):
    URLS = ['/api/v1/resource/get/<string:resource_id>']

    @rollback
    @check_auth(ROLE_USER)
    def get(self, resource_id):
        resource = BaseResource.get(resource_id)

        if resource and resource.resource.account_id in session['accounts']:
            return self.make_response({
                'message': None,
                'resource': resource
            })
        else:
            return self.make_response({
                'message': 'Resource not found or no access',
                'resource': None
            })


class ResourceGetChildren(BaseView):
    URLS = ['/api/v1/resource/children/<string:parent_id>']

    @rollback
    @check_auth(ROLE_USER)
    def get(self, parent_id):
        self.reqparse.add_argument('count', type=int, default=10)
        self.reqparse.add_argument('page', type=int, default=0)
        args = self.reqparse.parse_args()

        total, resources = BaseResource.find(limit=args.count, page=args.page, parent_id=parent_id)
        resources = [x.to_json() for x in resources]

        return self.make_response({
            'message': None,
            'resourceCount': total,
            'resources': resources
        })


class ResourceList(BaseView):
    URLS = ['/api/v1/resources']

    @rollback
    @check_auth(ROLE_USER)
    def get(self):
        self.reqparse.add_argument('count', type=int, default=25)
        self.reqparse.add_argument('page', type=int, default=0)
        self.reqparse.add_argument('keywords', type=str)
        self.reqparse.add_argument('resourceTypes', dest='resource_types', type=str, default=None, action='append')
        self.reqparse.add_argument('accounts', type=str, default=None, action='append')
        self.reqparse.add_argument('locations', type=str, default=None, action='append')
        self.reqparse.add_argument('partial', type=inputs.boolean, default=True)

        args = self.reqparse.parse_args()
        query = {
            'limit': args.count
        }
        resource_ids = []
        tags = {}
        properties = {}

        if args.keywords:
            for keyword in shlex.split(args.keywords):
                try:
                    if RGX_TAG.match(keyword):
                        groups = RGX_TAG.match(keyword).groupdict()

                        lx = shlex.shlex(groups['value'])
                        lx.whitespace = ['=']
                        lx.whitespace_split = True
                        key, values = list(lx)

                        vlx = shlex.shlex(re.sub(r'^"|"$', '', values))
                        vlx.whitespace = ['|']
                        vlx.whitespace_split = True
                        values = list(map(lambda x: int(x) if x.isnumeric() else x, list(vlx)))

                        tags[key] = values

                    elif RGX_PROPERTY.match(keyword):
                        groups = RGX_PROPERTY.match(keyword).groupdict()

                        lx = shlex.shlex(groups['value'])
                        lx.whitespace = ['=']
                        lx.whitespace_split = True
                        name, values = list(lx)

                        vlx = shlex.shlex(re.sub(r'^"|"$', '', values))
                        vlx.whitespace = ['|']
                        vlx.whitespace_split = True
                        values = list(map(lambda x: int(x) if x.isnumeric() else x, list(vlx)))

                        properties[from_camelcase(name)] = values

                    else:
                        resource_ids.append(keyword)

                except ValueError:
                    return self.make_response('Invalid formatted query', HTTP.BAD_REQUEST)

        qry = db.Resource.order_by(Resource.resource_type_id)

        if args.resource_types:
            qry = qry.join(ResourceType, Resource.resource_type_id == ResourceType.resource_type_id).filter(
                ResourceType.resource_type.in_(args.resource_types)
            )

        if resource_ids:
            id_rgx = '|'.join(x.lower() for x in resource_ids)
            if not is_truthy(args.partial):
                id_rgx = f'^({id_rgx})$'

            qry = qry.filter(Resource.resource_id.op('regexp')(id_rgx.lower()))

        if args.accounts:
            qry = qry.join(Account, Resource.account_id == Account.account_id).filter(
                Account.account_name.in_(args.accounts)
            )

        if args.locations:
            qry = qry.filter(Resource.location.in_(args.locations))

        if tags:
            for key, values in tags.items():
                alias = aliased(Tag)
                tqry = []
                qry = qry.join(alias, Resource.resource_id == alias.resource_id)

                rgx = '|'.join(x.lower() for x in values)
                if not is_truthy(args.partial):
                    rgx = f'^({rgx})$'

                tqry.append(
                    and_(
                        func.lower(alias.key) == key.lower(),
                        func.lower(alias.value).op('regexp')(rgx.lower())
                    )
                )

                qry = qry.filter(*tqry)

        if properties:
            for name, values in properties.items():
                alias = aliased(ResourceProperty)
                qry = qry.join(alias, Resource.resource_id == alias.resource_id)
                pqry = []

                if is_truthy(args.partial):
                    pqry.append(
                        and_(
                            func.lower(alias.name) == name.lower(),
                            or_(*(alias.value.ilike(f'%{v}%') for v in values))
                        )
                    )
                else:
                    pqry.append(
                        and_(
                            func.lower(alias.name) == name.lower(),
                            or_(*(func.JSON_CONTAINS(alias.value, v) for v in values))
                        )
                    )

                qry = qry.filter(*pqry)

        total = qry.count()
        qry = qry.limit(args.count)

        if args.page > 0:
            offset = args.page * args.count
            qry = qry.offset(offset)

        results = []
        for resource in qry.all():
            cls = current_app.types[resource.resource_type_id]
            data = cls(resource).to_json()
            results.append(data)

        if args.resource_types:
            query['resource_types'] = args.resource_types

        if args.accounts:
            query['accounts'] = args.accounts

        if args.locations:
            query['locations'] = args.locations

        if args.page:
            query['page'] = args.page

        return self.make_response({
            'message': None if results else 'No results found for this query',
            'resourceCount': total,
            'resources': results
        })
