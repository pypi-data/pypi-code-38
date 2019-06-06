#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata object class."""
import re
from cherrypy import tools, HTTPError
from pacifica.metadata.orm import Projects, ProjectUser
from pacifica.metadata.rest.project_queries.query_base import QueryBase
from pacifica.metadata.rest.userinfo import user_exists_decorator
from pacifica.metadata.orm.base import db_connection_decorator


class ProjectUserSearch(QueryBase):
    """ProjectUserSearch API."""

    exposed = True

    @staticmethod
    @user_exists_decorator
    def get_projects_for_user(user_id):
        """Return a list of formatted project objects for the indicated user."""
        # get list of project_ids for this user
        where_clause = ProjectUser().where_clause(
            {'user_id': user_id})
        # pylint: disable=no-member
        projects = (Projects
                    .select(
                        Projects.id, Projects.title, Projects.actual_start_date,
                        Projects.actual_end_date, Projects.closed_date,
                        Projects.accepted_date, Projects.submitted_date,
                        Projects.project_type
                    )
                    .join(ProjectUser)
                    .where(where_clause)
                    .order_by(Projects.title))
        # pylint: enable=no-member
        return [QueryBase.format_project_block(p) for p in projects if p]

    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @db_connection_decorator
    def GET(user_id=None):
        """Return a set of projects for a given user."""
        if user_id is not None:
            user_ids = re.findall('[0-9]+', user_id)
            if user_ids:
                user_id = int(user_ids.pop(0))
            else:
                raise HTTPError(
                    '400 Invalid User ID',
                    '"{0}" is not a valid user ID'.format(user_id)
                )
        else:
            raise HTTPError(
                '400 Invalid User ID',
                'No user ID specified'
            )

        return ProjectUserSearch.get_projects_for_user(user_id)
