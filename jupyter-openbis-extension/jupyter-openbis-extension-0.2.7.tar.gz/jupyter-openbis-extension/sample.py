from notebook.base.handlers import IPythonHandler
import numpy as np
import os
from .connection import openbis_connections
from urllib.parse import parse_qs


def get_entity_for_identifier(conn, identifier):
    entity = None
    try:
        entity = conn.openbis.get_sample(identifier)
    except Exception as exc:
        pass

    if entity is None:
        try:
            entity = conn.openbis.get_experiment(identifier)
        except Exception as exc:
            pass
    return entity


def get_datasets(entity, start_with=None, count=None):

    datasets = entity.get_datasets(start_with=start_with, count=count)
    totalCount = datasets.totalCount
    df = datasets.df
    df.replace({np.nan:None}, inplace=True)  # replace NaN with None, otherwise we cannot convert it correctly
    datasets_dict = df.to_dict(orient='records')   # is too stupid to handle NaN

    return {
        "datasets_dict": datasets_dict,
        "totalCount": totalCount
    }


class SampleHandler(IPythonHandler):
    """Handle the requests for /openbis/sample/connection/permId"""

    def get(self, **params):
        """Handle a request to /openbis/sample/connection_name/permId
        download the dataset list and return a message
        """
        try:
            conn = openbis_connections[params['connection_name']]
        except KeyError:
            self.set_status(500)
            self.write({
                "reason" : 'connection {} was not found'.format(
                    params['connection_name']
                )
            })
            return

        if not conn.is_session_active():
            try:
                conn.login()
            except Exception as exc:
                self.set_status(500)
                self.write({
                    "reason" : 'connection to {} could not be established: {}'.format(conn.name, exc)
                })
                return

        entity = get_entity_for_identifier(conn, params['identifier'])
        if entity is None:
            self.set_status(404)
            self.write({
                "reason" : 'No such Sample or Experiment: {}'.format(params['identifier'])
            })
            return None

        querystring = parse_qs(self.request.query)
        start_with = querystring.get('start_with', ['0'])[0]
        count      = querystring.get('count', ['10'])[0]

        datasets = get_datasets(entity, start_with=start_with, count=count)
        if datasets is not None:
            self.set_status(200)
            self.write({
                "dataSets"    : datasets.get('datasets_dict'),
                "entity_attrs": entity.attrs.all(),
                "entity_props": entity.props.all(),
                "start_with"  : start_with,
                "count"       : count,
                "totalCount"  : datasets.get('totalCount'),
                "cwd"         : os.getcwd()
            })

