# -*- coding: utf-8 -*-
import hmac
from hashlib import sha1
from uuid import UUID

from flask import current_app, request
from redis import Redis
from werkzeug.routing import BaseConverter

from cerberus import errors
from eve import Eve
from eve.auth import BasicAuth, HMACAuth, TokenAuth
from eve.io.base import BaseJSONEncoder
from eve.io.mongo import Mongo, Validator

redis = Redis()


class MyDataLayer(Mongo):
    def find(self, resource, req, sub_resource_lookup):
        sub_resource_lookup.pop("contact_id")
        return super(MyDataLayer, self).find(resource, req, sub_resource_lookup)


class BearerAuth(BasicAuth):
    """ Overrides Eve's built-in basic authorization scheme and uses Redis to
    validate bearer token.

    :param BasicAuth: Overriden Eve BasicAuth object
    """

    def check_auth(self, token, allowed_roles, resource, method):
        """ Check if API request is authorized.

        Examines token in header and checks Redis cache to see if token is
        valid. If so, request is allowed.
        :param token: OAuth 2.0 access token submitted.
        :param allowed_roles: Allowed user roles.
        :param resource: Resource being requested.
        :param method: HTTP method being executed (POST, GET, etc.)
        """
        return redis.get(token)

    def authorized(self, allowed_roles, resource, method):
        """ Validates the the current request is allowed to pass through.

        :param allowed_roles: allowed roles for the current request, can be a
                              string or a list of roles.
        :param resource: resource being requested.
        """
        try:
            token = request.headers.get("Authorization").split(" ")[1]
        except:
            token = None
        return token and self.check_auth(token, allowed_roles, resource, method)


class UUIDValidator(Validator):
    """
    Extends the base mongo validator adding support for the uuid data-type
    """

    def _validate_type_uuid(self, field, value):
        try:
            UUID(value)
        except ValueError:
            self._error(field, "value '%s' cannot be converted to a UUID" % value)


class UUIDConverter(BaseConverter):
    """
    UUID converter for the Werkzeug routing system.
    """

    def __init__(self, url_map):
        super(UUIDConverter, self).__init__(url_map)

    def to_python(self, value):
        return UUID(value)

    def to_url(self, value):
        return str(value)


# you can have multiple custom converters. Each converter has a key,
# which will be later used to designate endpoint urls, and a specialized
# BaseConverter subclass. In this case the url converter dictionary has
# only one item: our UUID converter.
url_converters = {"uuid": UUIDConverter}


class UUIDEncoder(BaseJSONEncoder):
    """ JSONEconder subclass used by the json render function.
    This is different from BaseJSONEoncoder since it also addresses
    encoding of UUID
    """

    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        else:
            # delegate rendering to base class method (the base class
            # will properly render ObjectIds, datetimes, etc.)
            return super(UUIDEncoder, self).default(obj)


class HMACAuth(HMACAuth):
    def check_auth(
        self, userid, hmac_hash, headers, data, allowed_roles, resource, method
    ):
        # use Eve's own db driver; no additional connections/resources are
        # used
        self.set_request_auth_value(userid)
        return userid == "root"
        # return True
        accounts = app.data.driver.db["accounts"]
        user = accounts.find_one({"userid": userid})
        if user:
            secret_key = user["secret_key"]
        # in this implementation we only hash request data, ignoring the
        # headers.
        return (
            user and hmac.new(str(secret_key), str(data), sha1).hexdigest() == hmac_hash
        )


class TAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
        return token == "token"


class Auth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource, method):
        # Check username and roles
        # accounts = app.data.driver.db['accounts']
        # lookup = {'username': 'nicola'}

        # if allowed_roles:
        #    lookup['roles'] = {'$in': allowed_roles}

        # account = accounts.find_one(lookup)
        # self.set_request_auth_value(username)
        return True


class Validator(Validator):
    def _validate_type_not_a_objectid(self, value):
        return True

    def _validate_empty(self, empty, field, value):
        super(Validator, self)._validate_empty(empty, field, value)
        if isinstance(value, list) and len(value) == 0 and not empty:
            self._error(field, errors.ERROR_EMPTY_NOT_ALLOWED)


def on_update(resoure, updates, original):
    updates["readonly"] = "change!"


def post_GET_callback(r, req, l):
    print(app.data.driver.db.activity.count())


def on_fetched_resource(resource, response):
    for doc in response["_items"]:
        doc["calculated_field"] = "hello"


v = Validator()


def on_insert(resource, items):
    import datetime

    for item in items:
        if "entry1" in item["entries"]:
            item["entries"]["entry1"] = datetime.datetime.now()


def on_aggregate(resource, pipeline):
    print(resource, pipeline)
    pipeline.append("ciao")


def pre_resource_get_handler(resource, request, lookup):
    lookup["$or"] = [{"name": "primo"}, {"name": "contact11"}]


def post_POST_callback(resource, request, response):
    print(resource, request, response)
    data = response.json
    del data["_issues"]
    del data["_error"]
    import json

    response.set_data(json.dumps(data))


app = Eve(validator=Validator)
import pdb; pdb.set_trace()  # XXX BREAKPOINT
app.test()
# app.on_post_POST += post_POST_callback
app.before_aggregation += on_aggregate
app.register_resource(
    "aggregate_test",
    {
        "datasource": {
            "aggregation": {
                "pipeline": [
                    {"$unwind": "$tags"},
                    {"$group": {"_id": "$tags", "count": {"$sum": "$field1"}}},
                ]
            }
        }
    },
)
# app.on_pre_GET += pre_resource_get_handler
# with app.test_request_context():
#    result = post_internal('contacts', {'name': 'Test1'})
# app.on_insert += on_insert
# app.config['BANDWIDTH_SAVER'] = False

if __name__ == "__main__":
    app.run(debug=True)
