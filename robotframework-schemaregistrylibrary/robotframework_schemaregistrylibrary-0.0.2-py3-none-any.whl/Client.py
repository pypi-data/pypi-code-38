import urllib.request
import urllib.error
import urllib.parse
import json
import sys
from avro import schema

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
        result = self.parse_schema_from_string(schema_str)
        return result

    def parse_schema_from_string(self, schema_str):
        """Parse a schema given a schema string"""
        return schema.Parse(schema_str)

    def parse_schema_from_file(self, schema_path):
        """Parse a schema from a file path"""
        with open(schema_path) as f:
            return parse_schema_from_string(f.read())

if __name__ == '__main__':
    Utils.parse_schema_from_string("test")
    print("test")
