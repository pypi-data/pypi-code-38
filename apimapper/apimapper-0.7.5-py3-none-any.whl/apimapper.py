import re
import requests
import logging
import json


from .config.config import *
from .responsemapper import ResponseMapper



class APIMapper:
    def __init__(self, source, mapping=None, timeout:float=0.1):
        # URL, result, mapping, filter
        self.source = source
        self.mapping = ResponseMapper(mapping)
        self.timeout = timeout
        if not self.source  or not self.source.get(URL):
            raise ValueError('Bad source, no URL')

        return

    def add_payload(self, payload_dict):
        if not self.source.get(PAYLOAD):
            self.source[PAYLOAD] = {}
            
        for k, v in payload_dict.items():
            self.source[PAYLOAD][k] = v
            
        return

    def set_payload(self, payload_dict):
        self.source[PAYLOAD] = payload_dict
        return

    def add_query(self, query):
        full_query = query
        if self.source.get(QUERY_PREFIX_WILDCARD, False):
            full_query = '*{}'.format(full_query)
        else:
            pass
        if self.source.get(QUERY_SUFFIX_WILDCARD, False):
            full_query = '{}*'.format(full_query)
        else:
            pass
                
        self.add_payload({self.source.get(QUERY_FIELD): full_query})
                             
        return
    
    def fetch_results(self, query=None):
        '''
        requests the url with the payload as specified in the source
        maps the response to the schema as specified in the source
        returns mapped_schema
        '''
        self.add_query(query)
            
        def get_response_content():
            '''
            analyses "original_response" - handles error codes and exceptions 
            and returns json decoded response from the result field if specified in the source
            or the complete response
            '''
            if  re.search(r'^2\d\d$', str(original_response.status_code)):
                try:
                    return json.loads(original_response.content)
            
                except Exception as e: # super bad!
                    logging.error('Cannot read API response, got %s', original_response.content)
                    logging.error(repr(e))
                    # Keep calm and carry on
            else:
                # bad status code in response
                logging.error('Bad request, got %s', original_response)

                
            return {}
        headers = {'accept': 'application/json'}
        try:
            original_response = requests.get(self.source.get(URL),
                                             params=self.source.get(PAYLOAD),
                                             headers=headers,
                                             timeout=self.source.get(TIMEOUT, self.timeout))
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout)  as ce:
            # Keep calm and carry on
            logging.error('Connection error while trying to access %s:\n %s',
                          self.source.get('URL'), repr(ce))
            return {}


        response_content = get_response_content()
        logging.debug(response_content)
        mapped_response = self.mapping.get_mapped_response(response_content)
        return mapped_response


