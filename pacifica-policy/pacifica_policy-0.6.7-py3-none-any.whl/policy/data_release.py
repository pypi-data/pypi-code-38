#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Data release policy for command line tools."""
from __future__ import print_function
from datetime import datetime
from json import dumps
from six import text_type
import requests
from dateutil import parser
from .config import get_config
from .admin import AdminPolicy
from .search.base import SearchBase

VALID_KEYWORDS = [
    'projects.actual_end_date',
    'projects.actual_start_date',
    'projects.submitted_date',
    'projects.accepted_date',
    'projects.closed_date',
    'transactions.created',
    'transactions.updated'
]


def collate_objs_from_key(resp, objs, date_key):
    """Deduplicate objs and make sure they have dates."""
    for chk_obj in resp.json():
        if chk_obj['_id'] not in objs.keys() and chk_obj.get(date_key, False):
            objs[chk_obj['_id']] = chk_obj[date_key]


def relavent_data_release_objs(time_ago, orm_obj, exclude_list):
    """Query projects or transactions that has gone past their suspense date."""
    trans_objs = set()
    suspense_args = {
        'suspense_date': 0,
        'suspense_date_0': (
            datetime.now() - time_ago
        ).replace(microsecond=0).isoformat(),
        'suspense_date_1': datetime.now().replace(microsecond=0).isoformat(),
        'suspense_date_operator': 'between'
    }
    suspense_args.update(SearchBase.global_get_args)
    resp = requests.get(
        text_type('{base_url}/{orm_obj}').format(
            base_url=get_config().get('metadata', 'endpoint_url'),
            orm_obj=orm_obj
        ),
        params=suspense_args
    )
    if orm_obj == 'projects':
        for proj_obj in resp.json():
            for rel_type in ['transsip', 'transsap']:
                proj_id = proj_obj['_id']
                if text_type(proj_id) in exclude_list:
                    continue
                resp = requests.get(
                    text_type('{base_url}/{rel_type}?project={proj_id}').format(
                        rel_type=rel_type,
                        base_url=get_config().get('metadata', 'endpoint_url'),
                        proj_id=proj_id
                    )
                )
                for trans_obj in resp.json():
                    trans_objs.add(trans_obj['_id'])
    else:
        for trans_obj in resp.json():
            if text_type(trans_obj['_id']) not in exclude_list:
                trans_objs.add(trans_obj['_id'])
    return trans_objs


def relavent_suspense_date_objs(time_ago, orm_obj, date_key):
    """generate a list of relavent orm_objs saving date_key."""
    objs = {}
    for time_field in ['updated', 'created']:
        obj_args = {
            'time_field': time_field,
            'epoch': (
                datetime.now() - time_ago
            ).replace(microsecond=0).isoformat()
        }
        obj_args.update(SearchBase.global_get_args)
        resp = requests.get(
            text_type('{base_url}/{orm_obj}').format(
                base_url=get_config().get('metadata', 'endpoint_url'),
                orm_obj=orm_obj
            ),
            params=obj_args
        )
        collate_objs_from_key(resp, objs, date_key)
    return objs


def update_suspense_date_objs(objs, time_after, orm_obj):
    """update the list of objs given date_key adding time_after."""
    for obj_id, obj_date_key in objs.items():
        resp = requests.post(
            text_type('{base_url}/{orm_obj}?_id={obj_id}').format(
                base_url=get_config().get('metadata', 'endpoint_url'),
                orm_obj=orm_obj,
                obj_id=obj_id
            ),
            data=dumps(
                {
                    '_id': obj_id,
                    'suspense_date': (
                        parser.parse(obj_date_key) + time_after
                    ).replace(microsecond=0).isoformat()
                }
            ),
            headers={'content-type': 'application/json'}
        )
        assert resp.status_code == 200


def update_data_release(objs):
    """Add objs transactions to the released transactions table."""
    admin_policy = AdminPolicy()
    rel_uuid = admin_policy.get_relationship_info(name='authorized_releaser')[0].get('uuid')
    for trans_id in objs:
        resp = requests.get(
            text_type(
                '{base_url}/transaction_user?transaction={trans_id}&relationship={rel_uuid}'
            ).format(
                base_url=get_config().get('metadata', 'endpoint_url'),
                trans_id=trans_id, rel_uuid=rel_uuid
            )
        )
        if resp.status_code == 200 and resp.json():
            continue
        resp = requests.put(
            text_type(
                '{base_url}/transaction_user'
            ).format(
                base_url=get_config().get('metadata', 'endpoint_url')
            ),
            data=dumps({
                'user': get_config().get('policy', 'admin_user_id'),
                'transaction': trans_id,
                'relationship': rel_uuid
            }),
            headers={'content-type': 'application/json'}
        )
        assert resp.status_code == 200


def data_release(args):
    """
    Data release main subcommand.

    The logic is to query updated objects between now and
    args.time_ago. If the objects args.keyword is set to something
    calculate the suspense date as args.time_after the keyword date.
    Then save the object back to the metadata server.

    The follow on task is to use orm_obj to calculate the released
    data based on the set suspense dates and add that released data
    to the transaction_release table.
    """
    orm_obj, date_key = args.keyword.split('.')
    objs = relavent_suspense_date_objs(args.time_ago, orm_obj, date_key)
    update_suspense_date_objs(objs, args.time_after, orm_obj)
    trans_objs = relavent_data_release_objs(
        args.time_ago, orm_obj, args.exclude)
    update_data_release(trans_objs)
