from enum import IntEnum, auto, Enum
from typing import Dict, List, Optional, Any


class AggsOrder(Enum):
    term = '_term'
    count = '_count'
    desc = 'desc'
    asc = 'asc'


class AggsType(Enum):
    terms = 'terms'
    _sum = 'sum'
    stats = 'stats'


class Operation(str, Enum):
    gte = 'gte'
    gt = 'gt'
    lte = 'lte'
    lt = 'lt'


class EsFormat(object):

    @classmethod
    def term_match_format(cls, value: str, key: str):
        return {
            "term": {
                key: {
                    "value": value
                }
            }
        }

    @classmethod
    def multi_match_format(cls, value: str, key: Optional[List[str]]=None):
        return {
            "multi_match": {
                "query": value,
                "fields": key if key else [],
            }
        }

    @classmethod
    def exists_format(cls, key: str):
        return {
            'exists': {
                'field': key,
            }
        }

    @classmethod
    def range_format(cls, key: str, **kwargs):
        op_dict: Dict[str, str] = dict()
        for _key, _value in kwargs.items():
            if _key not in Operation.__members__:
                raise ValueError('请输入正确的操作符')
            op_dict[_key] = _value

        return {
            'range': {
                key: op_dict
            }
        }

    @classmethod
    def highlight_format(cls, *args):
        _hl: Dict[str, str] = {}
        for key in args:
            _hl.update({key: {}})
        return {
            'highlight': {
                'fields': _hl
            }
        }

    @classmethod
    def start_format(cls, start: int):
        return {
            'from': start,
        }

    @classmethod
    def query_format(cls, qs: Dict[str, Any]):
        return {
            'query': qs,
        }

    @classmethod
    def match_all_format(cls):
        return {
            'query': {
                'match_all': {},
            }
        }

    @classmethod
    def sort_format(cls, *args: List[str]):
        _format: Dict[str, Any] = {}
        sort_keys: Dict[str, Any] = _format.setdefault('sort', {})
        for key in args:
            if key.startswith('-'):
                key = key.split('-')[1]
                sort_keys.update({
                    key: {
                        'order': AggsOrder.desc.value,
                    }
                })
                continue
            else:
                sort_keys.update({
                    key: {
                        'order': AggsOrder.asc.value,
                    }
                })
        return _format


class QueryType(IntEnum):
    Nomal = auto()
    Term = auto()
    Exits = auto()
    Range = auto()


class Aggs(object):
    def __init__(
            self, agg_field: str, agg_type: str = AggsType.terms.value,
            bucket: str='keys', order: str=AggsOrder.count.value, isdesc: bool=True, iskeyword: bool=False,
            size: Optional[int]=None,
            script: Optional[str]=None,
            min_doc: Optional[int]=None):
        self._type = agg_type
        self.field: str = f'{agg_field}.keyword' if iskeyword else agg_field
        self.bucket: str = bucket
        self.order: str = order
        self.order_type: bool = AggsOrder.desc.value if isdesc else AggsOrder.asc.value
        self.iskeyword: bool = iskeyword
        self.size: Optional[int] = size
        self.script: Optional[str] = script

        self.min_doc = min_doc
        self.child_aggs: Optional[Aggs] = None

    def parse(self):
        _aggs: Dict[str, str] = {
            'aggs': {
                f'{self.bucket}': {
                    f'{self._type}': {
                    }
                }
            }
        }

        aggs_type: Dict[str, Any] = _aggs['aggs'][self.bucket][self._type]
        if self.script:
            aggs_type.update({
                'script': self.script,
            })
        if self.field:
            aggs_type.update({
                'field': self.field,
            })
        if self.size:
            aggs_type.update({
                'size': self.size
            })
        if self.order:
            aggs_type.update({
                'order': {f'{self.order}': self.order_type}
            })
        if self.min_doc is not None:
            aggs_type.update({
                'min_doc_count': self.min_doc,
            })

        if self.child_aggs:
            _aggs['aggs'][self.bucket].update(self.child_aggs.parse())
        return _aggs


class Query(object):

    def __init__(self):
        self._must = []
        self._must_not = []
        self._should = []
        self.__filter = []

    def _and(self, Q):
        self._must.append(Q)

    def _or(self, Q):
        self._should.append(Q)

    def _not(self, Q):
        self._must_not.append(Q)

    def _filter(self, Q):
        self.__filter.append(Q)

    def __and__(self, obj):
        new_object: Query = self._clone()
        new_object._and(self.parse())
        new_object._and(obj.parse())
        return new_object

    def __or__(self, obj):
        new_object: Query = self._clone()
        new_object._or(self.parse())
        new_object._or(obj.parse())
        return new_object

    def _clone(self, **kwargs):
        return self.__class__()

    def __bool__(self):
        return any([self._must, self._must_not, self.__filter, self._should])

    def parse(self):
        return {
            'bool': {
                'must': self._must,
                'must_not': self._must_not,
                'should': self._should,
                'filter': self.__filter,
            }
        }


class EsQ(object):
    def __init__(self, client, index, q_type: Optional[QueryType] = None, *args, **kwargs):
        self.using = client
        self.index = index
        self.args = args
        self.kwargs = kwargs
        self._qs: Query = self._clone(q_type, *args, **kwargs)
        self._query: Dict[str, Any] = dict()
        self._resp: Dict[str, Any] = dict()
        self._timeout: int = 10

        self._aggs: Optional[Aggs] = None
        self._last_aggs: Optional[Aggs] = None

    def parse(self, q_type: QueryType, *args, **kwargs) -> List[Dict[str, Any]]:
        if 'iskeyword' in kwargs:
            iskeyword = kwargs.pop('iskeyword')
        else:
            iskeyword = False
        data_list: List[Dict[str, Any]] = []
        for _query in args:
            if isinstance(_query, Query):
                data_list.append(_query.parse())
        if q_type == QueryType.Term:
            for k, v in kwargs.items():
                if iskeyword and isinstance(v, str):
                    k = f'{k}.keyword'
                data_list.append(EsFormat.term_match_format(key=k, value=v))
        elif q_type == QueryType.Nomal:
            keys = kwargs.setdefault('keys', [])
            value = kwargs.setdefault('value', '')
            data_list.append(EsFormat.multi_match_format(value=value, key=keys))
        elif q_type == QueryType.Exits:
            for key in args:
                data_list.append(EsFormat.exists_format(key=key))
        elif q_type == QueryType.Range:
            if 'key' not in kwargs:
                raise TypeError('range must key')
            key = kwargs.pop('key', '')
            if iskeyword:
                key = f'{key}.keyword'
            data_list.append(EsFormat.range_format(key=key, **kwargs))
        return data_list

    def query(self, q_type: QueryType, *args, **kwargs):
        for data in self.parse(q_type, *args, **kwargs):
            self._qs._and(data)
        return self

    def exclude(self, q_type: QueryType, *args, **kwargs):
        for data in self.parse(q_type, *args, **kwargs):
            self._qs._not(data)
        return self

    def filter(self, q_type: QueryType, *args, **kwargs):
        for data in self.parse(q_type, *args, **kwargs):
            self._qs._filter(data)
        return self

    def maybe(self, q_type: QueryType, *args, **kwargs):
        for data in self.parse(q_type, *args, **kwargs):
            self._qs._or(data)
        return self

    def _clone(self, q_type: QueryType, *args, **kwargs):
        _qs = Query()
        for data in self.parse(q_type, *args, **kwargs):
            _qs._and(data)
        return _qs

    def highlight(self, *args):
        self._query.update(EsFormat.highlight_format(*args))
        return self

    def order_by(self, *args):
        self._query.update(EsFormat.sort_format(*args))
        return self

    def aggs(self, aggs_key: str, **kwargs):
        if not self._aggs:
            self._aggs = Aggs(agg_field=aggs_key, **kwargs)
            self._last_aggs = self._aggs
        else:
            if 'order' in kwargs:
                order = kwargs.pop('order')
            else:
                order = None
            agg = Aggs(agg_field=aggs_key, order=order, **kwargs)
            self._last_aggs.child_aggs = agg
            self._last_aggs = agg
        return self

    def pn(self, start: int):
        self._query.update(EsFormat.start_format(start))
        return self

    def excute(self):
        self._resp = self.using.search(index=self.index, body=self.query_dict, request_timeout=self._timeout)
        return self._resp

    def clear(self):
        self._query.clear()

    def update(self, data: dict):
        self._query.update(data)

    @property
    def timemout(self):
        return self._timeout

    @timemout.setter
    def timeout(self, value: int):
        self._timeout = value
        return value

    @property
    def count(self):
        if not self._resp:
            self.excute()
        return self._resp['hits']['total']

    @property
    def qs(self):
        return self._qs.parse()

    @property
    def datas(self):
        if not self._resp:
            self.excute()
        return self._resp['hits']['hits']

    @property
    def aggs_datas(self):
        if not self._resp:
            self.excute()
        return self._resp['aggregations']['keys']['buckets']

    @property
    def response(self):
        if not self._resp:
            self.excute()
        return self._resp

    @property
    def query_dict(self):
        _query = EsFormat.query_format(self._qs.parse()) if self._qs else EsFormat.match_all_format()
        self._query.update(_query)
        if self._aggs:
            self._query.update(self._aggs.parse())
            self._query.update({
                'size': 0,
            })
        return self._query

    def __and__(self, obj):
        if not isinstance(obj, EsQ):
            raise TypeError(obj)
        if obj.index != self.index:
            raise TypeError('must as the same index')
        self._qs = self._qs & obj._qs
        return self

    def __or__(self, obj):
        if not isinstance(obj, EsQ):
            raise TypeError(obj)
        if obj.index != self.index:
            raise TypeError('must as the same index')
        self._qs = self._qs | obj._qs
        return self
