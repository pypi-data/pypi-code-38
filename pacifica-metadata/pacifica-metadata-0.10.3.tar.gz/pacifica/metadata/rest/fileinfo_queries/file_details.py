#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy File Details object class."""
from six import text_type
from cherrypy import tools, HTTPError, request
from pacifica.metadata.orm import Files


# pylint: disable=too-few-public-methods
class FileDetailsLookup(object):
    """Retrieves file details for a list of file id's."""

    exposed = True

    @staticmethod
    def _get_file_details(file_list):
        query = Files().select().where(Files.id << file_list)
        if query.count() == 0:
            message = 'No files from the list {0} were located'.format(
                file_list)
            raise HTTPError('404 Not Found', message)
        return [{
            'file_id': f.id,
            'relative_local_path': text_type('{0}/{1}').format(f.subdir.rstrip('/'), f.name),
            'file_size_bytes': f.size,
            'hashtype': f.hashtype,
            'hashsum': f.hashsum
        } for f in query]

    # Cherrypy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_in()
    @tools.json_out()
    def POST():
        """Return file details for the list of file id's."""
        file_list = request.json
        return FileDetailsLookup._get_file_details(file_list)
