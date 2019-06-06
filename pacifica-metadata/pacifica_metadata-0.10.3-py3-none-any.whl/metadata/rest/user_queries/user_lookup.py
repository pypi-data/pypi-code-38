#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata object class."""
import re
import cherrypy
from cherrypy import tools
from peewee import DoesNotExist
from pacifica.metadata.orm import Users
from pacifica.metadata.rest.user_queries.query_base import QueryBase
from pacifica.metadata.orm.base import db_connection_decorator


class UserLookup(QueryBase):
    """Retrieves detailed info for a given user."""

    exposed = True

    @staticmethod
    def get_user_info_block(person_id, option=None):
        """Return a formatted dictionary containing the details of a given user entry."""
        terms = re.findall(r'[^+ ,;]+', str(person_id))
        for term in terms:
            if re.match('[0-9]+', term):
                person_id = term
                break
        try:
            user_entry = (Users.get(Users.id == person_id))
        except DoesNotExist:
            message = 'No User with an ID of {0} was found'.format(person_id)
            raise cherrypy.HTTPError('404 Not Found', message)
        return_block = QueryBase.format_user_block(user_entry, option)
        return return_block

    # CherryPy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @cherrypy.expose
    @db_connection_decorator
    def GET(person_id=None, option=None):
        """Return the requested user information for a specific person_id."""
        if person_id is not None and re.match('[0-9]+', person_id):
            cherrypy.log.error('id lookup request')
            return UserLookup.get_user_info_block(person_id, option)
        else:
            cherrypy.log.error('invalid request')
            raise cherrypy.HTTPError(
                '400 Invalid Lookup Options',
                QueryBase.compose_help_block_message()
            )
