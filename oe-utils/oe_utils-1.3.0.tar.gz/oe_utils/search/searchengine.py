# -*- coding: utf-8 -*-
import json
import logging
import requests
from zope.interface import Interface, implementer
from oe_utils.data.data_transfer_objects import ResultDTO

log = logging.getLogger(__name__)
NOT_SET = object()


def load_searchquery_parameters(query_params, settings, user_acls=None):
    """
    Creates a query for the searchengine based on the provided params.

    :param query_params: the request params for the search action
    :param settings: settings dictionary
    :param user_acls: an acces list for role based filtering
    :returns: Een :class:`dict` query object for the searchengine
    """
    q = {
        'match_all': {}
    }
    return q


def default_mapper(result, settings):
    if "hits" in result:
        result = [r['_source'] for r in result["hits"]["hits"]]
        return result
    else:
        return []


class ISearchEngine(Interface):
    def add_to_index(system_token, object_type, object_id, object_data):
        """add an object to the index with a specific type"""

    def remove_from_index(system_token, object_type, object_id):
        """remove an object from the index"""

    def remove_from_index_by_query(system_token, object_field, object_value):
        """remove an object from the index by query"""

    def query(system_token, object_type=None, query=None, sort='', options=None):
        """execute a query on the search engine"""

    def remove_index(system_token):
        """remove the index"""

    def create_index(system_token, data=None):
        """create the index"""

    def add_type_mapping(object_type, object_type_mapping, system_token):
        """add the mapping for specific type"""


@implementer(ISearchEngine)
class SearchEngine(object):
    def __init__(self, baseurl, index_name, version='1'):
        self.baseurl = baseurl
        self.index_name = index_name
        self.version = version
        self.content_header = {"Content-Type": "application/json"} if self.version == '6' else {}

    def add_to_index(self, system_token, object_type, object_id, object_data):
        """add an object to the index with a specific type"""
        headers = {'OpenAmSSOID': system_token} if system_token else {}
        headers.update(self.content_header)
        res = requests.put(self.baseurl + '/' + self.index_name + '/' + object_type + '/' + str(object_id),
                           object_data, headers=headers)
        res.raise_for_status()

    def bulk_add_to_index(self, system_token, object_type, data, id_field='id',
                          batch_size=5000):
        """
        Adds the given iterable of data to the elasticsearch index in bulk.

        The _id being set at elasticsearch is taken from the "id_field" in
        each json dict. If the key is not found, no _id will be set and
        Elasticsearch will generate one.

        :param system_token: OpenAmSSOID header for request to Elasticsearch
        :param object_type: The type to add the index to.
        :param data: An iterable of json dicts to add to the index.
        :param id_field: The field in the data which should become the _id in
                         Elasticsearch
        :param batch_size: Maximum amount of items to send per batch.
        :return:
        """
        bulk_url = (self.baseurl + '/' + self.index_name +
                    '/' + object_type + '/_bulk')
        batch_data = ''
        for i, item in enumerate(data, start=1):
            action = {'index': {}}
            if id_field in item:
                action['index']['_id'] = item[id_field]
            batch_data += json.dumps(action) + '\n' + json.dumps(item) + '\n'
            if i % batch_size == 0:
                self._send_batch(system_token, bulk_url, batch_data)
                batch_data = ''
        if batch_data:
            self._send_batch(system_token, bulk_url, batch_data)

    def _send_batch(self, system_token, bulk_url, batch_data):
        headers = {'OpenAmSSOID': system_token} if system_token else {}
        if self.version not in ('1', '2', '3', '4'):
            headers['Content-Type'] = 'application/x-ndjson'
        res = requests.put(bulk_url, data=batch_data, headers=headers)
        res.raise_for_status()

    def remove_from_index(self, system_token, object_type, object_id):
        """remove an object from the index"""
        headers = {'OpenAmSSOID': system_token} if system_token else {}
        res = requests.delete(self.baseurl + '/' + self.index_name + '/' + object_type + '/' + str(object_id),
                              headers=headers)
        res.raise_for_status()

    def remove_from_index_by_query(self, system_token, object_field, object_value):
        """remove an object from the index by query"""
        headers = {'OpenAmSSOID': system_token} if system_token else {}
        if self.version == '1':
            res = requests.delete(self.baseurl + '/' + self.index_name +
                                  '/_query?q=' + object_field + ':' + str(object_value),
                                  headers=headers)
        else:
            headers.update(self.content_header)
            delete_query = {"query": {"match": {object_field: object_value}}}
            res = requests.post(self.baseurl + '/' + self.index_name + '/_delete_by_query',
                                data=json.dumps(delete_query),
                                headers=headers)
        res.raise_for_status()

    def query(self, system_token, object_type=None, query_params=None, sort=None, result_range=None,
              mapper=default_mapper, load_searchquery_param_func=load_searchquery_parameters,
              aggregations=None, settings=None, user_acls=None, min_score=None,
              principals=NOT_SET):
        """execute a query on the search engine"""
        query = load_searchquery_param_func(query_params, settings, user_acls=user_acls)
        if not sort:
            sort = ['_score']
        params = {}
        if result_range:
            params['size'] = result_range.get_page_size()
            params['from'] = result_range.start
        data = {
            "query": query,
            "sort": sort,
        }
        if min_score:
            data["min_score"] = min_score
        if aggregations:
            data["aggregations"] = aggregations
        headers = {'OpenAmSSOID': system_token} if system_token else {}
        headers.update(self.content_header)
        search_url = self.baseurl + "/" + self.index_name
        # if no object_type assume full index search
        search_url += '/' + object_type + '/_search' if object_type else '/_search'
        res = requests.post(search_url, data=json.dumps(data), params=params, headers=headers)
        res.raise_for_status()
        result = json.loads(res.text)
        mapper_args = [result, settings]
        if principals != NOT_SET:
            mapper_args.append(principals)
        return ResultDTO(mapper(*mapper_args),
                         result["hits"]["total"] if "hits" in result else 0,
                         result["aggregations"] if "aggregations" in result else None)

    def remove_index(self, system_token):
        headers = {'OpenAmSSOID': system_token} if system_token else {}
        res = requests.head(self.baseurl + "/" + self.index_name, headers=headers)
        if res.status_code < 400:  # otherwise assume index doens't exists
            res = requests.delete(self.baseurl + "/" + self.index_name, headers=headers)
            res.raise_for_status()

    def create_index(self, system_token, data):
        headers = {'OpenAmSSOID': system_token} if system_token else {}
        headers.update(self.content_header)
        res = requests.put(self.baseurl + "/" + self.index_name, data=json.dumps(data), headers=headers)
        res.raise_for_status()

    def add_type_mapping(self, object_type, object_type_mapping, system_token):
        headers = {'OpenAmSSOID': system_token} if system_token else {}
        headers.update(self.content_header)
        res = requests.put(self.baseurl + "/" + self.index_name + "/_mapping/" + object_type,
                           data=json.dumps(object_type_mapping), headers=headers)
        res.raise_for_status()
