"""
Constants used in api project
"""
from marshmallow.fields import (
    Raw, Nested, Dict, List, String, UUID, Number, Integer, Decimal, Boolean, FormattedString,
    Float, DateTime, LocalDateTime, Time, Date, TimeDelta, Url, URL, Email, Str, Bool, Int, Constant
)

############################################################
# Marshmallow's field categories
############################################################
MARSHMALLOW_LIST_FIELDS = (List,)
MARSHMALLOW_NESTED_FIELDS = (Nested,)
MARSHMALLOW_DICT_FIELDS = (Dict,)
MARSHMALLOW_SCALAR_FIELDS = (
    Raw, Constant,
    UUID, String, Str, FormattedString, str,
    Number, Integer, Int, int, Decimal,
    Boolean, Bool, bool,
    Float, float,
    Date, DateTime, LocalDateTime, Time, TimeDelta,
    Email, URL, Url,
    # Function, Method
)

############################################################
# Mongo operator customie mapping
############################################################
MONGO_LOOKUPS_MAPPINGS = {

    # comparison query operators
    'eq': '$eq',
    'ne': '$ne',
    'lt': '$lt',
    'lte': '$lte',
    'gt': '$gt',
    'gte': '$gte',
    'nin': '$nin',
    'in': '$in',

    # logical query operators
    'and': '$and',
    'not': '$not',
    'nor': '$nor',
    'or': '$or',

    # element query operators
    'exists': '$exists',
    'type': '$type',

    # evaluation query operators
    'expr': '$expr',
    'json_schema': '$jsonSchema',
    'mod': '$mod',
    'regex': '$regex',
    'text': '$text',
    'where': '$where',

    # array query operators
    'all': '$all',
    'elem_match': '$elemMatch',
    'size': '$size',

    # bitwise query operators
    'bits_all_clear': '$bitsAllClear',
    'bits_all_set': '$bitsAllSet',
    'bits_any_clear': '$bitsAnyClear',
    'bits_any_set': '$bitsAnySet',

    # 'elemmatch': '$elemmatch',

    # TODO: there are more other operaters need to introduce here
    # ...
}

############################################################
# Separator which used to separate request's field & operator
############################################################
REQUEST_LOOKUP_MARK = '__'
MONGO_RANGE_OPERATOR_SET = ['$in', '$nin']
REQUEST_LIST_SEP = ','
POTENTIAL_MONGO_ID_FIELD_NAME = 'id'

############################################################
# Mark to indicate sort a field by desc order
############################################################
REQUEST_DESC_SORT_MARK = '-'

############################################################
# Request's query string's constants
############################################################
SORT_KEY = 'sort'
PAGE_KEY = 'page'
LIMIT_KEY = 'limit'
PROJECTION_KEY = 'projection'
SKIP_KEY = 'skip'

############################################################
# Database constants
############################################################
RECORD_ACTIVE_FLAG_FIELD = '_enabled'
MONGO_ID_FIELD_NAME = '_id'

############################################################
# HTTP messages
############################################################
HTTP_OK = 'OK'
HTTP_DELETE_OK = 'Delete Success'
HTTP_UPDATE_OK = 'Update Success'
