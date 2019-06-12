import json
import yaml
import time
from wrappers import SONATAClient 
from pytest import fixture
from .sonata_fixture import * 
from .config import *

def test_auth(auth_keys):
	"""Tests API call to fetch Auth token"""
	sonata_auth = SONATAClient.Auth(HOST_URL)
	response = json.loads(sonata_auth.auth(
							username=USERNAME,
							password=PASSWORD))
	response = json.loads(response["data"])

	assert isinstance(response, dict)
	assert set(auth_keys).issubset(
				response.keys()), "All keys should be in the response"

def __init__(self):
	pass