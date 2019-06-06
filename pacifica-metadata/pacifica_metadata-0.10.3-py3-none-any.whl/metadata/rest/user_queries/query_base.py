#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata projectinfo base class."""
from pacifica.metadata.orm import UserGroup, Projects, ProjectUser


class QueryBase(object):
    """Retrieves a set of projects for a given keyword set."""

    @staticmethod
    def format_user_block(user_entry, option=None):
        """Construct a dictionary from a given user instance in the metadata stack."""
        user_hash = user_entry.to_hash()
        project_xref = ProjectUser()
        where_exp = project_xref.where_clause({'user': user_entry.id})
        project_person_query = (
            ProjectUser.select().where(where_exp)).dicts()

        project_list = [proj['project'] for proj in project_person_query]

        clean_projects = {}

        if project_list:
            projects = Projects.select(
                Projects.id, Projects.title, Projects.short_name,
                Projects.project_type, Projects.science_theme
            ).where(
                Projects.id << project_list).dicts()

            for proj in projects:
                proj_id = proj['id']
                clean_projects[proj_id] = proj

        display_name = u'[User ID {0}] {1} {2} &lt;{3}&gt;'.format(
            user_entry.id,
            user_hash.get('first_name'),
            user_hash.get('last_name'),
            user_hash.get('email_address')
        )
        if option != 'simple':
            return_block = {
                'category': user_hash.get('last_name')[:1],
                'person_id': user_hash.get('_id'),
                'first_name': user_hash.get('first_name'),
                'last_name': user_hash.get('last_name'),
                'network_id': user_hash.get('network_id'),
                'email_address': user_hash.get('email_address'),
                'last_updated': user_hash.get('updated'),
                'display_name': display_name,
                'simple_display_name': u'{0} {1}'.format(
                    user_hash.get('first_name'), user_hash.get('last_name')),
                'emsl_employee': False,
                'projects': clean_projects
            }
        else:
            return_block = {
                'person_id': user_hash.get('_id'),
                'first_name': user_hash.get('first_name'),
                'last_name': user_hash.get('last_name'),
                'display_name': u'{0} {1}'.format(
                    user_hash.get('first_name'),
                    user_hash.get('last_name')
                ),
                'email_address': user_hash.get('email_address'),
                'emsl_employee': False
            }

        return_block['emsl_employee'] = QueryBase._is_admin_user(user_entry)

        return return_block

    @staticmethod
    def _is_admin_user(user_entry):
        is_admin = False
        where_exp = UserGroup().where_clause({'person_id': user_entry.id})
        for group in UserGroup.select().where(where_exp):
            if group.person_id == user_entry.id:
                is_admin = True
                break
        return is_admin

    @staticmethod
    def compose_help_block_message():
        """Assemble a block of relevant help text to be returned with an invalid request."""
        message = 'You must supply either a numeric person id (like "/userinfo/<person_id>")'
        message += ' or search for one using the form '
        message += '"/userinfo/search/<search_term_1>+<search_term_2>"'
        return message
