#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
The CherryPy rest object for the structure.

Below is an example post body::

    [
        {"destinationTable": "Transactions._id", "value": 1234},
        {"destinationTable": "Transactions.submitter", "value": 34002},
        {"destinationTable": "Transactions.project", "value": "34002"},
        {"destinationTable": "Transactions.instrument", "value": 34002},
        {"destinationTable": "TransactionKeyValue", "key": "Tag", "value": "Blah"},
        {"destinationTable": "TransactionKeyValue", "key": "Taggy", "value": "Blah"},
        {"destinationTable": "TransactionKeyValue", "key": "Taggier", "value": "Blah"}
        {
            "destinationTable": "Files",
            "_id": 34, "name": "foo.txt", "subdir": "a/b/",
            "ctime": "Tue Nov 29 14:09:05 PST 2016",
            "mtime": "Tue Nov 29 14:09:05 PST 2016",
            "size": 128, "mimetype": "text/plain"
        },
        {
            "destinationTable": "Files",
            "_id": 35, "name": "bar.txt", "subdir": "a/b/",
            "ctime": "Tue Nov 29 14:09:05 PST 2016",
            "mtime": "Tue Nov 29 14:09:05 PST 2016",
            "size": 47, "mimetype": "text/plain"
        },
    ]
"""
from six import text_type
from cherrypy import tools, request, HTTPError
from pacifica.policy.uploader.rest import UploaderPolicy


# pylint: disable=too-few-public-methods
class IngestPolicy(UploaderPolicy):
    """CherryPy Ingest Policy Class."""

    @staticmethod
    def _pull_data_by_rec(query, table):
        """Pull the value for the table."""
        for rec in query:
            if rec['destinationTable'] == table:
                return rec['value']
        return None

    def _valid_query(self, query):
        """Validate the metadata format."""
        variables_to_query = {
            'submitter': 'users',
            'project': 'projects',
            'instrument': 'instruments'
        }
        invalid_terms = []
        valid_terms = {}
        for variable in variables_to_query:
            value = self._pull_data_by_rec(
                query, 'Transactions.{0}'.format(variable))
            valid = self._object_id_valid(variables_to_query[variable], value)
            if not valid:
                invalid_terms.append(variable)
            else:
                valid_terms[variable] = value
        if not invalid_terms:
            # all the incoming terms are valid, check for xrefs
            if text_type(valid_terms['project']) not in self._projects_for_user_inst(
                    valid_terms['submitter'], valid_terms['instrument']):
                invalid_terms.append(
                    text_type('project ({}) not in user instrument list ({})').format(
                        text_type(valid_terms['project']),
                        self._projects_for_user_inst(
                            valid_terms['submitter'],
                            valid_terms['instrument']
                        )
                    )
                )
            if int(valid_terms['instrument']) not in self._instruments_for_user_proj(
                    valid_terms['submitter'], valid_terms['project']
            ):
                invalid_terms.append(
                    text_type('instrument ({}) not in user project list ({})').format(
                        int(valid_terms['instrument']),
                        self._instruments_for_user_proj(
                            valid_terms['submitter'],
                            valid_terms['project']
                        )
                    )
                )
            if not invalid_terms:
                return {'status': 'success'}

        raise HTTPError(412, text_type(
            'Precondition Failed: Invalid values for {0}').format(', '.join(invalid_terms)))

    # pylint: disable=invalid-name
    @tools.json_in()
    @tools.json_out()
    def POST(self):
        """Read in the json query and return results."""
        metadata = request.json
        return self._valid_query(metadata)
    # pylint: enable=invalid-name
# pylint: enable=too-few-public-methods
