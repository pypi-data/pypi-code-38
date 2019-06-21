#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Base class module for standard queries for the upload status tool."""
from pacifica.policy.config import get_config
from pacifica.policy.admin import AdminPolicy


# pylint: disable=too-few-public-methods
class QueryBase(AdminPolicy):
    """This pulls the common bits of instrument and project query into a single class."""

    md_url = get_config().get('metadata', 'endpoint_url')
    all_instruments_url = '{0}/instruments'.format(md_url)
    all_projects_url = '{0}/projects'.format(md_url)
    all_transactions_url = '{0}/transactions'.format(md_url)

    def _get_available_projects(self, user_id):
        return self._projects_for_user(user_id)
# pylint: enable=too-few-public-methods
