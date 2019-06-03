import json
import yaml
import time
from wrappers import OSMClient 
from pytest import fixture
from .osm_fixture import * 
from .config import *

def test_auth(auth_keys):
	"""Tests API call to fetch Auth token"""
	osm_c = OSMClient.Auth(HOST_URL)
	response = json.loads(osm_c.auth(username=USERNAME, password=PASSWORD))
	response = json.loads(response["data"])

	assert isinstance(response, dict)
	assert set(auth_keys).issubset(
				response.keys()), "All keys should be in the response"
