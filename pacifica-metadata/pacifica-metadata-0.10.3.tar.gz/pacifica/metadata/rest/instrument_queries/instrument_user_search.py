#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata object class."""
from cherrypy import tools
from pacifica.metadata.orm import Instruments, ProjectUser, ProjectInstrument
from pacifica.metadata.rest.instrument_queries.query_base import QueryBase
from pacifica.metadata.rest.userinfo import user_exists_decorator
from pacifica.metadata.orm.base import db_connection_decorator


class InstrumentUserSearch(QueryBase):
    """InstrumentUserSearch API."""

    exposed = True

    @staticmethod
    @user_exists_decorator
    def get_instruments_for_user(user_id):
        """Return a list of formatted instrument objects for the indicated user."""
        where_clause = ProjectUser().where_clause(
            {'user': user_id})

        instrument_list = (Instruments
                           .select()
                           .distinct()
                           .join(ProjectInstrument,
                                 on=(ProjectInstrument.instrument == Instruments.id))
                           .join(ProjectUser,
                                 on=(ProjectUser.project == ProjectInstrument.project))
                           .where(where_clause)
                           .order_by(Instruments.display_name))
        return [QueryBase.format_instrument_block(obj) for obj in instrument_list]

    # pylint: disable=invalid-name
    # pylint: disable=duplicate-code
    @staticmethod
    @tools.json_out()
    @db_connection_decorator
    def GET(user_id):
        """Return a set of instruments for a given user."""
        inst_list = InstrumentUserSearch.get_instruments_for_user(
            user_id=user_id)
        return inst_list
