import urllib.request
import urllib.error
import urllib.parse
import json
import sys
from avro import schema
import Utils

class SchemaRegistryClient(object):
    def __init__(self, url):
        self.url = url.rstrip('/')

    def _send_get_request(self, url, headers=None):
        request = urllib.request.Request(url)
        request.add_header('Accept', 'application/vnd.schemaregistry.v1+json')
        response = urllib.request.urlopen(request)
        result = json.loads(response.read())
        return result

    def _set_subject(self, subject):
        subject_suffix = '-value'
        if (subject.endswith("-value")):
            subject = subject
        else:
            subject= subject + subject_suffix
        return subject

    def get_latest_schema(self, subject):
        subject = self._set_subject(subject)
        schema_api_url =   "%s/subjects/%s/versions/latest/" % (self.url, subject)
        result = self._send_get_request(schema_api_url)
        return result['id'], result['schema'], result['version']

    def get_by_id(self, schema_id):
        url = "%s/schemas/ids/%s/" % (self.url, str(schema_id))
        result = self._send_get_request(url)
        schema_str = result.get("schema")
        result = Utils.parse_schema_from_string(schema_str)
        return result
