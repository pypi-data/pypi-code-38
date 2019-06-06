#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Usersearch object class."""
import re
import cherrypy
from cherrypy import tools
from peewee import OP, Expression, fn
from pacifica.metadata.orm import Users
from pacifica.metadata.rest.user_queries.query_base import QueryBase
from pacifica.metadata.orm.base import db_connection_decorator


class UserSearch(QueryBase):
    """Retrieves detailed info for a given user."""

    exposed = True

    @staticmethod
    def search_for_user(search_term, option):
        """Return a dictionary containing information about a given user."""
        terms = re.findall(r'[^+ ,;]+', search_term)
        keys = ['first_name', 'last_name', 'network_id', 'email_address', 'id']
        where_clause = Expression(1, OP.EQ, 1)
        for user_term in terms:
            user_term = str(user_term)
            where_clause_part = Expression(1, OP.EQ, 0)
            for k in keys:
                if k == 'id':
                    if re.match('[0-9]+', user_term):
                        where_clause_part |= Expression(
                            Users.id, OP.EQ, user_term)
                        where_clause_part |= (
                            fn.TO_CHAR(Users.id, '99999999999').contains(
                                user_term)
                        )
                else:
                    where_clause_part |= (
                        getattr(Users, k).contains(user_term)
                    )
            where_clause &= (where_clause_part)
        objs = Users.select().where(where_clause).order_by(
            Users.last_name, Users.first_name)
        if not objs:
            message = "No user entries were retrieved using the terms: '"
            message += '\' and \''.join(terms) + '\''
            raise cherrypy.HTTPError('404 No Valid Users Located', message)

        return [QueryBase.format_user_block(obj, option) for obj in objs]

    # CherryPy requires these named methods.
    # pylint: disable=invalid-name, unused-argument
    @staticmethod
    @tools.json_out()
    @cherrypy.expose
    @db_connection_decorator
    def GET(search_term=None, option=None, **kwargs):
        """Return the requested user information for a given set of search criteria."""
        if search_term is not None and search_term:
            cherrypy.log.error('search request')
            return UserSearch.search_for_user(search_term, option)
        else:
            cherrypy.log.error('invalid request')
            raise cherrypy.HTTPError(
                '400 Invalid Request Options',
                QueryBase.compose_help_block_message()
            )
