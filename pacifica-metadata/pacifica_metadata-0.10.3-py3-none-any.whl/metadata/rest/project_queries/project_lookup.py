#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata object class."""
import re
import cherrypy
from cherrypy import tools, HTTPError
from peewee import DoesNotExist
from pacifica.metadata.orm import Projects, Instruments, ProjectInstrument
from pacifica.metadata.rest.project_queries.query_base import QueryBase
from pacifica.metadata.orm.base import db_connection_decorator


class ProjectLookup(QueryBase):
    """Retrieves a set of projects for a given keyword set."""

    exposed = True

    @staticmethod
    def _get_project_details(project_id):
        """Return a formatted dictionary containing the details of a given Project entry."""
        terms = re.findall(r'[^+ ,;]+', str(project_id))
        for term in terms:
            # Take the first thing that matches standard project id numbering
            if re.match('[0-9]+[a-z]?', term):
                project_id = term
                break
        try:
            project_entry = (Projects.get(Projects.id == project_id))
        except DoesNotExist:
            message = 'No Project with an ID of {0} was found'.format(
                project_id)
            raise HTTPError('404 Not Found', message)

        proj_inst = ProjectInstrument()
        pi_where_clause = proj_inst.where_clause(
            {'project_id': project_id})
        instrument_entries = (Instruments
                              .select(
                                  Instruments.id, Instruments.display_name,
                                  Instruments.name, Instruments.name_short,
                                  Instruments.active
                              )
                              .order_by(Instruments.id)
                              .join(ProjectInstrument)
                              .where(pi_where_clause))
        instruments = {i.id: {
            'id': i.id,
            'display_name': i.display_name,
            'name': i.name,
            'name_short': i.name_short,
            'active': i.active
        } for i in instrument_entries}

        return QueryBase.format_project_block(project_entry, instruments)

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @db_connection_decorator
    def GET(project_id=None):
        """CherryPy GET method."""
        if project_id is not None and re.match('[0-9]+[a-z]*', project_id):
            cherrypy.log.error('project details request')
            return ProjectLookup._get_project_details(project_id)
        else:
            message = 'Invalid project details lookup request. '
            message += "'{0}' is not a valid project_id".format(
                project_id)
            cherrypy.log.error(message)
            raise HTTPError(
                status='400 Invalid Request Options',
                message=QueryBase.project_help_block_message()
            )
