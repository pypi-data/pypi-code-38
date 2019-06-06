#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Metadata Migration Class for Instrument Entities."""
from cherrypy import tools
from peewee import prefetch
from pacifica.metadata.orm import Instruments
from pacifica.metadata.orm import ProjectInstrument
from pacifica.metadata.rest.instrument_queries.query_base import QueryBase as InstQueryBase


class MigrateInstruments(object):
    """Generate a streamlined query for importing instrument entities and linkages."""

    exposed = True

    @staticmethod
    def generate_instrument_list():
        """Generate instrument objects with linkages."""
        instrument_list = {}
        inst_collection = (Instruments
                           .select(Instruments)
                           .order_by(Instruments.id)
                           .where(Instruments.deleted.is_null()))

        project_collection = (ProjectInstrument.select(
        ).order_by(ProjectInstrument.project))

        instruments_with_projects = prefetch(
            inst_collection, project_collection)

        for inst in instruments_with_projects:
            inst_entry = InstQueryBase.format_instrument_block(inst)
            inst_entry['projects'] = [
                proj.project.id for proj in inst.projects]
            instrument_list[inst.id] = inst_entry

        return instrument_list

    # CherryPy requires these named methods
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    def GET():
        """CherryPy GET Method."""
        return MigrateInstruments.generate_instrument_list()
