#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Search base class has some common data and logic."""
try:
    from functools import lru_cache
except ImportError:  # pragma: no cover only python 2
    from backports.functools_lru_cache import lru_cache
from functools import wraps
from six import text_type
import requests
from ..admin import AdminPolicy
from ..config import get_config


_LRU_GLOBAL_ARGS = {
    'maxsize': get_config().getint('policy', 'cache_size'),
    'typed': False
}


def search_lru_cache(func):
    """Wrap a function with my lru cache args."""
    @lru_cache(**_LRU_GLOBAL_ARGS)
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Calling inter function."""
        return func(*args, **kwargs)
    return wrapper


class SearchBase(object):
    """Search base class containing common data and logic."""

    fields = []
    rel_objs = []
    obj_type = 'unimplemented'
    releaser_uuid = AdminPolicy().get_relationship_info(name='authorized_releaser')[0].get('uuid')
    search_required_uuid = AdminPolicy().get_relationship_info(name='search_required')[0].get('uuid')
    global_get_args = {
        'recursion_depth': '0',
        'recursion_limit': '1'
    }

    @classmethod
    @search_lru_cache
    def get_rel_by_args(cls, mdobject, **kwargs):
        """Get the transaction user relationship."""
        get_params = kwargs.copy()
        get_params.update(cls.global_get_args)
        resp = requests.get(
            text_type('{base_url}/{mdobject}').format(
                mdobject=mdobject,
                base_url=get_config().get('metadata', 'endpoint_url')
            ),
            params=get_params
        )
        assert resp.status_code == 200
        return resp.json()

    @classmethod
    def get_transactions(cls, **kwargs):  # pragma: no cover abstract method
        """Unimplemented in the base class."""
        raise NotImplementedError

    @classmethod
    def _transsip_transsap_merge(cls, trans_obj, key):
        ret = set()
        for trans_rel in ['transsip', 'transsap']:
            for rel_trans_obj in cls.get_rel_by_args(trans_rel, **trans_obj):
                ret.update([rel_trans_obj[key]])
        return ret

    @staticmethod
    def _cls_name_to_module(rel_cls):
        """Convert the class name to the object type and module to load."""
        return rel_cls.__module__.split('.')[-1]

    @classmethod
    def render(cls, obj, render_rel_objs=False, render_trans_ids=False):
        """Render the object and return it."""
        ret = {'type': cls._cls_name_to_module(cls)}
        for key in cls.fields:
            ret[key] = getattr(cls, key)(**obj)
        if render_rel_objs:
            for related_obj_name in cls.rel_objs:
                ret[related_obj_name] = getattr(cls, '{}_obj_lists'.format(related_obj_name))(**obj)
        if render_trans_ids:
            ret['transaction_ids'] = cls.get_transactions(**obj)
        return ret
