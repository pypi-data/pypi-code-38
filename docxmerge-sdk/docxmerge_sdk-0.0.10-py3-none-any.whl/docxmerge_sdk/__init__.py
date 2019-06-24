import json

import requests


class Docxmerge:
    def __init__(self, apikey="", host="https://api.docxmerge.com"):
        self.api_key = apikey
        self.base_url = host
        self.http_client = requests.Session()
        self.http_client.headers["api-key"] = apikey

    def transform_template(self, template_name):
        transform_template_url = self.base_url + '/api/v1/Admin/TransformTemplate?template=' + template_name
        response = self.http_client.get(transform_template_url)
        if response.status_code == 404:
            raise Exception("Template %s not found" % template_name)
        if response.status_code != 200:
            raise Exception("Bad status code %d" % response.status_code)
        return response.content

    def transform_file(self, file):
        transform_file_url = self.base_url + '/api/v1/Admin/TransformFile'
        response = self.http_client.post(transform_file_url, files={'file': file})
        if response.status_code != 200:
            raise Exception("Bad status code %d" % response.status_code)
        return response.content

    def merge_template(self, template_name, data):
        merge_template_url = self.base_url + '/api/v1/Admin/MergeTemplate?template=' + template_name
        response = self.http_client.post(merge_template_url, json=data)
        if response.status_code == 404:
            raise Exception("Template %s not found" % template_name)
        if response.status_code != 200:
            raise Exception("Bad status code %d" % response.status_code)
        return response.content

    def merge_file(self, file, data):
        merge_file_url = self.base_url + '/api/v1/Admin/MergeFile'
        dumps = json.dumps(data)
        response = self.http_client.post(merge_file_url,
                                         data={'data': dumps},
                                         files={'file': file}
                                         )
        if response.status_code != 200:
            raise Exception("Bad status code %d" % response.status_code)
        return response.content

    def merge_and_transform_template(self, template_name, data):
        merge_template_url = self.base_url + '/api/v1/Admin/MergeAndTransformTemplatePost?template=' + template_name
        response = self.http_client.post(merge_template_url, json=data)
        if response.status_code == 404:
            raise Exception("Template %s not found" % template_name)
        if response.status_code != 200:
            raise Exception("Bad status code %d" % response.status_code)
        return response.content
        pass

    def merge_and_transform_file(self, file, data):
        merge_file_url = self.base_url + '/api/v1/Admin/MergeAndTransform'
        dumps = json.dumps(data)
        response = self.http_client.post(merge_file_url,
                                         data={'data': dumps},
                                         files={'file': file}
                                         )
        if response.status_code != 200:
            raise Exception("Bad status code %d" % response.status_code)
        return response.content
