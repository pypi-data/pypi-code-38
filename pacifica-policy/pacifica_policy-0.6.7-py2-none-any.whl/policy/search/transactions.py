#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Search transaction rendering methods."""
from six import text_type
from ..config import get_config
from .users import UsersRender
from .institutions import InstitutionsRender
from .instruments import InstrumentsRender
from .groups import GroupsRender
from .projects import ProjectsRender
from .science_themes import ScienceThemesRender
from .keys import KeysRender
from .values import ValuesRender
from .files import FilesRender
from .base import SearchBase


class TransactionsRender(SearchBase):
    """Render a transaction for search."""

    fields = [
        'obj_id', 'access_url', 'has_doi', 'release',
        'updated_date', 'created_date', 'description'
    ]
    rel_objs = [
        'users', 'institutions', 'instruments', 'groups',
        'projects', 'science_themes', 'key_value_pairs', 'files'
    ]

    @staticmethod
    def obj_id(**trans_obj):
        """Return string for object id."""
        return text_type('transactions_{_id}').format(**trans_obj)

    @staticmethod
    def description(**trans_obj):
        """Return string for the updated date."""
        return text_type('{description}').format(**trans_obj)

    @staticmethod
    def updated_date(**trans_obj):
        """Return string for the updated date."""
        return text_type('{updated}').format(**trans_obj)

    @staticmethod
    def created_date(**trans_obj):
        """Return string for the created date."""
        return text_type('{created}').format(**trans_obj)

    @classmethod
    def release(cls, **trans_obj):
        """Return 'true' if transaction has been release."""
        if cls.get_rel_by_args('transaction_user', transaction=trans_obj['_id'], relationship=cls.releaser_uuid):
            return 'true'
        return 'false'

    @classmethod
    def access_url(cls, **trans_obj):
        """Figure out the access url for the transaction."""
        trans_doi = cls.get_trans_doi(trans_obj['_id'])
        if trans_doi != 'false':
            trans_obj['doi'] = trans_doi
            return get_config().get('policy', 'doi_url_format').format(**trans_obj)
        if cls.release(**trans_obj) == 'true':
            return get_config().get('policy', 'release_url_format').format(**trans_obj)
        return get_config().get('policy', 'internal_url_format').format(**trans_obj)

    @classmethod
    def get_trans_doi(cls, trans_id):
        """Get the transaction doi or return false."""
        trans_user = cls.get_rel_by_args('transaction_user', transaction=trans_id, relationship=cls.releaser_uuid)
        if not trans_user:
            return 'false'
        rel_uuid = trans_user[0].get('uuid')
        doi_trans = cls.get_rel_by_args('doi_transaction', transaction=rel_uuid)
        if doi_trans:
            return doi_trans[0].get('doi', 'false')
        return 'false'

    @classmethod
    def has_doi(cls, **trans_obj):
        """Return boolean if the transaction has a DOI."""
        if cls.get_trans_doi(trans_obj['_id']) != 'false':
            return 'true'
        return 'false'

    @classmethod
    def files_obj_lists(cls, **trans_obj):
        """Get the projects related to the transaction."""
        return [
            FilesRender.render(file_obj)
            for file_obj in cls.get_rel_by_args('files', transaction=trans_obj['_id'])
        ]

    @classmethod
    def users_obj_lists(cls, **trans_obj):
        """Get the user objects and relationships."""
        ret = {'submitter': []}
        for user_id in cls._transsip_transsap_merge({'_id': trans_obj['_id']}, 'submitter'):
            ret['submitter'].append(
                UsersRender.render(cls.get_rel_by_args('users', _id=user_id)[0])
            )
        for trans_user_obj in cls.get_rel_by_args('transaction_user', transaction=trans_obj['_id']):
            rel_obj = cls.get_rel_by_args('relationships', uuid=trans_user_obj['relationship'])[0]
            rel_list = ret.get(rel_obj['name'], [])
            rel_list.append(
                UsersRender.render(cls.get_rel_by_args('users', _id=trans_user_obj['user'])[0])
            )
            ret[rel_obj['name']] = rel_list
        return ret

    @classmethod
    def institutions_obj_lists(cls, **trans_obj):
        """Get the institutions related to the transaction."""
        ret = set()
        user_id_list = cls._transsip_transsap_merge({'_id': trans_obj['_id']}, 'submitter')
        user_id_list.update([obj['user'] for obj in cls.get_rel_by_args(
            'transaction_user', transaction=trans_obj['_id'])])
        for user_id in user_id_list:
            for inst_obj in cls.get_rel_by_args('institution_user', user=user_id):
                ret.update([inst_obj['institution']])
        return [
            InstitutionsRender.render(
                cls.get_rel_by_args('institutions', _id=inst_id)[0]
            ) for inst_id in ret
        ]

    @classmethod
    def instruments_obj_lists(cls, **trans_obj):
        """Get the instruments related to the transaction."""
        ret = set()
        for trans_obj in cls.get_rel_by_args('transsip', _id=trans_obj['_id']):
            ret.update([trans_obj['instrument']])
        return [
            InstrumentsRender.render(
                cls.get_rel_by_args('instruments', _id=inst_id)[0]
            ) for inst_id in ret
        ]

    @classmethod
    def groups_obj_lists(cls, **trans_obj):
        """Get the instrument groups related to the transaction."""
        ret = set()
        for inst_obj in cls.get_rel_by_args('transsip', _id=trans_obj['_id']):
            for group_obj in cls.get_rel_by_args('instrument_group', instrument=inst_obj['instrument']):
                ret.update([group_obj['group']])
        return [
            GroupsRender.render(
                cls.get_rel_by_args('groups', _id=group_id)[0]
            ) for group_id in ret
        ]

    @classmethod
    def projects_obj_lists(cls, **trans_obj):
        """Get the projects related to the transaction."""
        return [
            ProjectsRender.render(
                cls.get_rel_by_args('projects', _id=proj_id)[0]
            ) for proj_id in cls._transsip_transsap_merge({'_id': trans_obj['_id']}, 'project')
        ]

    @classmethod
    def science_themes_obj_lists(cls, **trans_obj):
        """Get science themes related to the transaction."""
        return [
            ScienceThemesRender.render(
                cls.get_rel_by_args('projects', _id=proj_id)[0]
            ) for proj_id in cls._transsip_transsap_merge({'_id': trans_obj['_id']}, 'project')
        ]

    @classmethod
    def key_value_pairs_obj_lists(cls, **trans_obj):
        """Get the key value pairs related to the transaction."""
        ret = {
            'key_value_hash': {},
            'key_objs': [],
            'value_objs': []
        }
        for trans_kvp_obj in cls.get_rel_by_args('trans_key_value', transaction=trans_obj['_id']):
            key_obj = cls.get_rel_by_args('keys', _id=trans_kvp_obj['key'])[0]
            value_obj = cls.get_rel_by_args('values', _id=trans_kvp_obj['value'])[0]
            ret['key_objs'].append(KeysRender.render(key_obj))
            ret['value_objs'].append(ValuesRender.render(value_obj))
            ret['key_value_hash'][key_obj['key']] = value_obj['value']
        return ret

    # this doesn't get executed but is needed to be here to satisfy abstract method
    @classmethod
    def get_transactions(cls, **_trans_obj):  # pragma: no cover
        """Just return an empty list."""
        return []
