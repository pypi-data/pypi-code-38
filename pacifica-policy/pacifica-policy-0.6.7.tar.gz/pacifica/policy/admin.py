#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The Admin module has logic about checking for admin group info."""
from __future__ import absolute_import
from json import loads
import requests
from .config import get_config

RECURSION_DEPTH = 0


# pylint: disable=too-few-public-methods
class AdminPolicy(object):
    """
    Enforces the admin policy.

    Base class for checking for admin group membership or not.
    """

    md_url = get_config().get('metadata', 'endpoint_url')
    all_users_url = '{0}/users'.format(md_url)
    all_instruments_url = '{0}/instruments'.format(md_url)
    all_projects_url = '{0}/projects'.format(md_url)
    all_relationships_url = '{0}/relationships'.format(md_url)
    proj_user_url = '{0}/project_user'.format(md_url)
    proj_instrument_url = '{0}/project_instrument'.format(md_url)
    inst_user_url = '{0}/instrument_user'.format(md_url)
    inst_group_url = '{0}/instrument_group'.format(md_url)

    def __init__(self):
        """Constructor for Uploader Policy."""
        self.admin_group = get_config().get('policy', 'admin_group')
        self.admin_group_id = get_config().get('policy', 'admin_group_id')

    def _format_url(self, url, **get_args):
        """Append the recursion_depth parameter to the url."""
        get_args['recursion_depth'] = RECURSION_DEPTH
        args_str = '&'.join(
            [u'{0}={1}'.format(key, value) for key, value in get_args.items()]
        )
        return u'{0}?{1}'.format(getattr(self, url), args_str)

    def get_relationship_info(self, **get_args):
        """Get a relationship by kwargs."""
        return loads(requests.get(self._format_url('all_relationships_url', **get_args)).text)

    def _all_project_info(self):
        return loads(requests.get(self._format_url('all_projects_url')).text)

    def _all_instrument_info(self):
        return loads(requests.get(self._format_url('all_instruments_url')).text)

    def _projects_for_user(self, user_id, relationship='member_of'):
        if self._is_admin(user_id):
            return [proj['_id'] for proj in self._all_project_info()]
        rel_uuid = self.get_relationship_info(name=relationship)[0].get('uuid')
        proj_url = self._format_url('proj_user_url', user=user_id, relationship=rel_uuid)
        return [part['project'] for part in loads(requests.get(proj_url).text)]

    def _projects_for_custodian(self, user_id):
        inst_list = self._instruments_for_custodian(user_id)
        projects_for_custodian = set([])
        for inst in inst_list:
            projects = self._projects_for_inst(inst)
            projects_for_custodian = projects_for_custodian.union(projects)
        return list(projects_for_custodian)

    def _instruments_for_custodian(self, user_id):
        rel_uuid = self.get_relationship_info(name='custodian')[0].get('uuid')
        inst_custodian_associations_url = self._format_url(
            'inst_user_url', user=user_id, relationship=rel_uuid)
        inst_custodian_list = loads(requests.get(
            inst_custodian_associations_url).text)
        return [i['instrument'] for i in inst_custodian_list]

    def _projects_for_inst(self, inst_id):
        inst_projs_url = self._format_url(
            'proj_instrument_url',
            instrument_id=inst_id
        )
        inst_projs = loads(requests.get(inst_projs_url).text)
        inst_projs = set([part['project'] for part in inst_projs])
        return inst_projs

    def _projects_for_user_inst(self, user_id, inst_id):
        projs = set(self._projects_for_user(user_id))
        projs_for_custodian = set(self._projects_for_custodian(user_id))
        inst_groups = self._groups_for_inst(inst_id)
        if inst_groups:
            group_insts = set()
            for group_id in inst_groups:
                group_insts |= set(self._instruments_for_group(group_id))
        else:
            group_insts = set([inst_id])
        ginst_projs = set()
        for ginst_id in group_insts:
            ginst_projs |= self._projects_for_inst(ginst_id)
        return list((projs | projs_for_custodian) & ginst_projs)

    def _project_info_from_ids(self, proj_list):
        ret = []
        if proj_list:
            for proj_id in proj_list:
                proj_url = self._format_url('all_projects_url', _id=proj_id)
                ret.extend(loads(requests.get(proj_url).text))
        return ret

    def _groups_for_inst(self, inst_id):
        inst_g_url = self._format_url('inst_group_url', instrument_id=inst_id)
        return [i['group'] for i in loads(requests.get(inst_g_url).text)]

    def _instruments_for_group(self, group_id):
        inst_g_url = self._format_url('inst_group_url', group_id=group_id)
        return [i['instrument'] for i in loads(requests.get(inst_g_url).text)]

    def _instruments_for_user(self, user_id):
        if self._is_admin(user_id):
            return [inst['_id'] for inst in self._all_instrument_info()]
        return self._instruments_for_custodian(user_id)

    def _instruments_for_user_proj(self, user_id, proj_id):
        user_insts = set(self._instruments_for_user(user_id))
        if self._is_admin(user_id):
            return list(user_insts)
        proj_insts_url = self._format_url(
            'proj_instrument_url', project=proj_id)
        proj_insts = set([part['instrument']
                          for part in loads(requests.get(proj_insts_url).text)])
        inst_groups = set()
        for inst_id in proj_insts:
            inst_groups |= set(self._groups_for_inst(inst_id))
        group_insts = set()
        for group_id in inst_groups:
            group_insts |= set(self._instruments_for_group(group_id))
        return list(group_insts | user_insts | proj_insts)

    def _instrument_info_from_ids(self, inst_list):
        ret = []
        for inst_id in inst_list:
            inst_url = self._format_url('all_instruments_url', _id=inst_id)
            ret.extend(loads(requests.get(inst_url).text))
        return ret

    def _users_for_proj(self, proj_id):
        user_proj_url = self._format_url(
            'proj_user_url', project=proj_id)
        user_projs = loads(requests.get(user_proj_url).text)
        return list(set([str(part['user']) for part in user_projs]))

    def _user_info_from_kwds(self, **kwds):
        return loads(requests.get(self._format_url('all_users_url', **kwds)).text)

    @staticmethod
    def _object_id_valid(object_lookup_name, object_id):
        if not object_id:
            return False
        object_type_url = '{0}/{1}'.format(get_config().get('metadata', 'endpoint_url'),
                                           object_lookup_name)
        object_query_url = u'{0}?_id={1}'.format(object_type_url, object_id)
        object_value_req = requests.get(object_query_url)
        object_is_valid = loads(object_value_req.text)
        return len(object_is_valid) > 0

    def _is_admin(self, user_id):
        amember_query = '{0}/user_group?group={1}&person={2}'.format(
            self.md_url,
            self.admin_group_id,
            user_id
        )
        is_admin_req = requests.get(amember_query)
        is_admin_list = loads(is_admin_req.text)
        return len(is_admin_list) > 0
# pylint: enable=too-few-public-methods
