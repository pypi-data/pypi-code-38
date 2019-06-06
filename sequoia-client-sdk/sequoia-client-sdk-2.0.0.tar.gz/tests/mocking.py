import requests_mock
import re
import os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


def bootstrap_mock():
    adapter = requests_mock.Adapter()
    register_identity_mappings(adapter)
    register_registry_mappings(adapter)
    register_validation_mappings(adapter)
    return adapter


def register_identity_mappings(adapter):
    add_post_mapping_for(adapter, "identity", "valid_identity_response")


def register_registry_mappings(adapter):
    add_get_mapping_for(adapter, "registry", "valid_registry_response")


def register_validation_mappings(adapter):
    add_post_mapping_for(adapter, "validation", "valid_validation_response")


def add_get_mapping_for(mock, service, filepath):
    matcher = re.compile('.*%s.*' % service)
    with open(__location__ + "/test_files/%s.json" % filepath) as file:
        mock.register_uri('GET', matcher, text=file.read())


def add_get_mapping_for_url(mock, url, filepath):
    matcher = re.compile('.*%s.*' % url)
    with open(__location__ + "/test_files/%s.json" % filepath) as file:
        mock.register_uri('GET', matcher, text=file.read())


def add_post_mapping_for(mock, service, filepath):
    matcher = re.compile('.*%s.*' % service)
    with open(__location__ + "/test_files/%s.json" % filepath) as file:
        mock.register_uri('POST', matcher, text=file.read())


def add_put_mapping_for(mock, service, filepath):
    matcher = re.compile('.*%s.*' % service)
    with open(__location__ + "/test_files/%s.json" % filepath) as file:
        mock.register_uri('PUT', matcher, text=file.read())


def add_delete_mapping_for(mock, service):
    matcher = re.compile('.*%s.*' % service)
    mock.register_uri('DELETE', matcher, text="{}")
