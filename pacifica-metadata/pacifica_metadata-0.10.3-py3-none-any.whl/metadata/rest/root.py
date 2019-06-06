#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy root object class."""
from json import dumps
import cherrypy
from pacifica.metadata.orm.all_objects import ORM_OBJECTS
from pacifica.metadata.rest.objectinfo import ObjectInfoAPI
from pacifica.metadata.rest.userinfo import UserInfoAPI
from pacifica.metadata.rest.projectinfo import ProjectInfoAPI
from pacifica.metadata.rest.transactioninfo import TransactionInfoAPI
from pacifica.metadata.rest.fileinfo import FileInfoAPI
from pacifica.metadata.rest.ingest import IngestAPI
from pacifica.metadata.rest.instrumentinfo import InstrumentInfoAPI
from pacifica.metadata.rest.summaryinfo import SummaryInfoAPI
from pacifica.metadata.rest.migrationinfo import MigrationInfoAPI
from pacifica.metadata.rest.tkvinfo import TkvInfoAPI
from pacifica.metadata.rest.tkvupload import TkvUploadAPI
from pacifica.metadata.rest.doiupload import DOIUploadAPI


def error_page_default(**kwargs):
    """The default error page should always enforce json."""
    cherrypy.response.headers['Content-Type'] = 'application/json'
    return dumps({
        'status': kwargs['status'],
        'message': kwargs['message'],
        'traceback': kwargs['traceback'],
        'version': kwargs['version']
    })


# pylint: disable=too-few-public-methods
class Root(object):
    """
    CherryPy root object class.

    not exposed by default the base objects are exposed
    """

    exposed = True

    objectinfo = ObjectInfoAPI()
    userinfo = UserInfoAPI()
    projectinfo = ProjectInfoAPI()
    fileinfo = FileInfoAPI()
    transactioninfo = TransactionInfoAPI()
    instrumentinfo = InstrumentInfoAPI()
    summaryinfo = SummaryInfoAPI()
    ingest = IngestAPI()
    migrate = MigrationInfoAPI()
    tkvinfo = TkvInfoAPI()
    tkvupload = TkvUploadAPI()
    doiupload = DOIUploadAPI()

    @staticmethod
    @cherrypy.tools.json_out()
    # pylint: disable=invalid-name
    def GET():
        """Return happy message about functioning service."""
        return {'message': 'Pacifica Metadata Up and Running'}
    # pylint: enable=invalid-name
# pylint: enable=too-few-public-methods


for cls in ORM_OBJECTS:
    # this is based on the module name being something like pacifica.metadata.orm.BLAH
    obj_loc = cls.__module__.split('.')[3]
    setattr(Root, obj_loc, cls())
