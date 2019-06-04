#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Class for the archive interface.

Allows API to file interactions for passed in archive backends.
"""
from __future__ import print_function
import shutil
from json import dumps
import cherrypy
from .archive_utils import get_http_modified_time, file_status, bytes_type
from .exception import ArchiveInterfaceError

BLOCK_SIZE = 1 << 20


def error_page_default(**kwargs):
    """The default error page should always enforce json."""
    cherrypy.response.headers['Content-Type'] = 'application/json'
    return dumps({
        'status': kwargs['status'],
        'message': kwargs['message'],
        'traceback': kwargs['traceback'],
        'version': kwargs['version']
    })


class ArchiveInterfaceGenerator(object):
    """Archive Interface Generator.

    Defines the methods that can be used on files for request types.
    """

    exposed = True

    def __init__(self, archive):
        """Create an archive interface generator."""
        self._archive = archive
        self._response = None
        print('Pacifica Archive Interface Up and Running')

    # pylint: disable=invalid-name
    def GET(self, *args):
        """Get a file from WSGI request.

        Gets a file specified in the request and writes back the data.
        """
        # if asking for / then return a message that the archive is working
        if not args:
            cherrypy.response.headers['Content-Type'] = 'application/json'
            return bytes_type(dumps({'message': 'Pacifica Archive Interface Up and Running'}))
        archivefile = self._archive.open(args[0], 'r')
        cherrypy.response.headers['Content-Type'] = 'application/octet-stream'

        def read():
            """Read the data from the file."""
            buf = archivefile.read(BLOCK_SIZE)
            while buf:
                yield buf
                buf = archivefile.read(BLOCK_SIZE)
        return read()
    # as documented in cherrypy wiki
    # pylint: disable=protected-access
    GET._cp_config = {'response.stream': True}
    # pylint: enable=protected-access
    # pylint: enable=invalid-name

    @cherrypy.tools.json_out()
    # pylint: disable=invalid-name
    def PUT(self, filepath):
        """Write a file from WSGI requests.

        Writes a file passed in the request to the archive.
        """
        mod_time = get_http_modified_time(cherrypy.request.headers)
        archivefile = self._archive.open(filepath, 'w')
        try:
            content_length = int(
                cherrypy.request.headers.get('Content-Length'))
        except Exception as ex:  # pragma: no cover it's hard to get a client to not do this
            raise ArchiveInterfaceError(
                "Can't get file content length with error: {}".format(str(ex))
            )
        shutil.copyfileobj(cherrypy.request.body, archivefile)
        archivefile.close()
        archivefile.set_mod_time(mod_time)
        archivefile.set_file_permissions()
        cherrypy.response.status = '201 Created'
        return {'message': 'File added to archive', 'total_bytes': content_length}
    # pylint: enable=invalid-name

    # pylint: disable=invalid-name
    def HEAD(self, filepath):
        """Get the file status from WSGI request.

        Gets the status of a file specified in the request.
        """
        archivefile = self._archive.open(filepath, 'r')
        status = archivefile.status()
        file_status(status, cherrypy.response)
        archivefile.close()
    # pylint: enable=invalid-name

    @cherrypy.tools.json_out()
    # pylint: disable=invalid-name
    def POST(self, filepath):
        """Stage a file from WSGI request.

        Stage the file specified in the request to disk.
        """
        archivefile = self._archive.open(filepath, 'r')
        archivefile.stage()
        archivefile.close()
        cherrypy.response.status = '200 OK'
        return {'message': 'File was staged', 'file': filepath}
    # pylint: enable=invalid-name

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    # pylint: disable=invalid-name
    def PATCH(self, filepath):
        """Move a file from the original path to the new one specified."""
        file_path = cherrypy.request.json['path']
        file_id = filepath
        self._archive.patch(file_id, file_path)
        cherrypy.response.status = '200 OK'
        return {'message': 'File Moved Successfully'}
    # pylint: enable=invalid-name

    # pylint: disable=invalid-name
    def DELETE(self, filepath):
        """Delete a file from WSGI request.

        Delete the file specified in the request to disk.
        """
        archivefile = self._archive.open(filepath, 'r')
        archivefile.close()
        archivefile.remove()
        cherrypy.response.status = '200 OK'
    # pylint: enable=invalid-name
