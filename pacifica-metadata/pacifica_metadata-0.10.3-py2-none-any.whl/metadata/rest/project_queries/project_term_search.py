#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata object class."""
import re
import cherrypy
from cherrypy import tools
from peewee import OP, Expression
from pacifica.metadata.orm import Projects
from pacifica.metadata.rest.project_queries.query_base import QueryBase
from pacifica.metadata.orm.base import db_connection_decorator


class ProjectTermSearch(QueryBase):
    """ProjectTermSearch API."""

    exposed = True

    @staticmethod
    def search_for_project(search_term):
        """Return a dictionary containing information about a given project."""
        terms = re.findall(r'[^+ ,;]+', search_term)
        keys = ['title', 'id']
        where_clause = Expression(1, OP.EQ, 1)
        for term in terms:
            term = str(term)
            where_clause_part = Expression(1, OP.EQ, 0)
            for k in keys:
                if k == 'id':
                    if re.match('[0-9]+[a-z]?', term):
                        where_clause_part |= (
                            Projects.id == term
                        )
                        where_clause_part |= (
                            Projects.id.contains(term)
                        )
                else:
                    where_clause_part |= (
                        getattr(Projects, k).contains(term)
                    )
            where_clause &= (where_clause_part)
        objs = Projects.select().where(where_clause).order_by(Projects.title)
        if not objs:
            message = 'No project entries were retrieved using the terms: \''
            message += '\' and \''.join(terms) + '\''
            raise cherrypy.HTTPError('404 No Valid Projects Located', message)

        return [QueryBase.format_project_block(obj) for obj in objs]

    # pylint: disable=invalid-name
    # pylint: disable=duplicate-code
    @staticmethod
    @tools.json_out()
    @db_connection_decorator
    def GET(search_term=None):
        """Return a set of projects for a given user."""
        if search_term is not None:
            return ProjectTermSearch.search_for_project(search_term)
        else:
            raise cherrypy.HTTPError(
                '400 No Search Terms Provided',
                QueryBase.project_help_block_message()
            )
