#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata object class."""
import cherrypy
from cherrypy import tools
from pacifica.metadata.orm import TransSIP
from pacifica.metadata.rest.project_queries.query_base import QueryBase
from pacifica.metadata.orm.base import db_connection_decorator


class ProjectHasData(QueryBase):
    """Does the project have data for instruments."""

    exposed = True

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @tools.json_in()
    @db_connection_decorator
    def POST():
        """CherryPy GET method."""
        ret_hash = {}
        for project_id in cherrypy.request.json:
            ret_hash[project_id] = []
            instlist = [trans.instrument for trans in TransSIP.select(
                TransSIP.instrument
            ).where(
                TransSIP.project == project_id
            ).distinct()]
            for instrument in instlist:
                data = [x.created for x in TransSIP.select(
                    TransSIP.created
                ).where(
                    (TransSIP.project == project_id) &
                    (TransSIP.instrument == instrument)
                ).order_by(
                    TransSIP.created.desc()
                ).limit(10)]
                ret_hash[project_id].append({
                    'instrument': instrument.id,
                    'end_time': data[0].isoformat(),
                    'start_time': data[-1].isoformat(),
                    'num_results': len(data)
                })
        return ret_hash
