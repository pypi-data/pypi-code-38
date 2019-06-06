#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Metadata Migration Class for Instrument Entities."""
from cherrypy import tools
from peewee import prefetch
from pacifica.metadata.orm import Projects
from pacifica.metadata.orm import ProjectInstrument, ProjectUser
from pacifica.metadata.rest.project_queries.query_base import QueryBase as ProjQueryBase


class MigrateProjects(object):
    """Generate a streamlined query for importing project entities and linkages."""

    exposed = True

    @staticmethod
    def generate_project_list():
        """Generate project objects with linkages."""
        project_list = {}
        proj_collection = (Projects
                           .select()
                           .order_by(Projects.id)
                           .where(Projects.deleted.is_null()))
        instrument_collection = (ProjectInstrument.select(
        ).order_by(ProjectInstrument.instrument))
        user_collection = (ProjectUser.select(
        ).order_by(ProjectUser.user))

        projects_with_links = prefetch(
            proj_collection, instrument_collection, user_collection)

        for proj in projects_with_links:
            proj_entry = ProjQueryBase.format_project_block(proj)
            proj_entry['abstract'] = proj.abstract
            proj_entry['instruments'] = [
                inst.instrument.id for inst in proj.instruments]
            proj_entry['users'] = [
                user_entry.user.id for user_entry in proj.users]
            project_list[proj.id] = proj_entry

        return project_list

    # CherryPy requires these named methods
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    def GET():
        """CherryPy GET Method."""
        return MigrateProjects.generate_project_list()
