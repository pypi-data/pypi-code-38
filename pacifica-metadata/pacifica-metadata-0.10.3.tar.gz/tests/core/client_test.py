#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test class for the client api."""
from unittest import TestCase
from json import dumps, loads
import httpretty
from pacifica.metadata.orm.utils import unicode_type
from pacifica.metadata.client import PMClient, PMClientError


class TestClient(TestCase):
    """Test client class."""

    @httpretty.activate
    def test_client_get(self):
        """Test the client get methods."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        params = {
            '_id': 127
        }
        response_body = {
            '_id': 127,
            'last_name': 'Doe',
            'first_name': 'John',
            'network_id': 'johndoe'
        }
        httpretty.register_uri(httpretty.GET, '{0}/{1}'.format(endpoint_url, class_type),
                               body=dumps(response_body),
                               content_type='application/json')
        client = PMClient(endpoint_url)
        response = client.get(class_type, params)
        self.assertNotEqual(response, {})
        for key in response.keys():
            self.assertEqual(response[key], response_body[key])

    @httpretty.activate
    def test_client_get_not_found(self):
        """Test response from the client when the object is not found."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        params = {
            '_id': 127
        }
        response_body = {}
        httpretty.register_uri(httpretty.GET, '{0}/{1}'.format(endpoint_url, class_type),
                               body=dumps(response_body),
                               content_type='application/json',
                               status=404)
        client = PMClient(endpoint_url)
        response = client.get(class_type, params)
        self.assertEqual(response, {})

    @httpretty.activate
    def test_client_get_server_error(self):
        """Test the client response to an internal server error."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        params = {
            '_id': 127
        }
        httpretty.register_uri(httpretty.GET, '{0}/{1}'.format(endpoint_url, class_type),
                               body='This is the error.',
                               status=501)
        client = PMClient(endpoint_url)
        try:
            client.get(class_type, params)
        except PMClientError as ex:
            self.assertTrue('501' in str(ex))
            self.assertTrue('This is the error.' in str(ex))

    @httpretty.activate
    def test_client_get_unknown_error(self):
        """Test the client response to an unknown error."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        params = {
            '_id': 127
        }
        httpretty.register_uri(httpretty.GET, '{0}/{1}'.format(endpoint_url, class_type),
                               body='This is the error.',
                               status=301)
        client = PMClient(endpoint_url)
        try:
            client.get(class_type, params)
        except PMClientError as ex:
            self.assertTrue('301' in str(ex))
            self.assertTrue('This is the error.' in str(ex))

    @httpretty.activate
    def test_client_delete(self):
        """Test the client response to an unknown error."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        params = {
            '_id': 127
        }
        httpretty.register_uri(
            httpretty.DELETE, '{0}/{1}'.format(endpoint_url, class_type))
        client = PMClient(endpoint_url)
        response = client.delete(class_type, params)
        self.assertTrue(response)

    @httpretty.activate
    def test_client_delete_notfound(self):
        """Test the client response to an unknown error."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        params = {
            '_id': 127
        }
        httpretty.register_uri(
            httpretty.DELETE, '{0}/{1}'.format(endpoint_url, class_type), status=404)
        client = PMClient(endpoint_url)
        response = client.delete(class_type, params)
        self.assertTrue(response)

    @httpretty.activate
    def test_client_delete_server_error(self):
        """Test the client response to an unknown error."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        params = {
            '_id': 127
        }
        httpretty.register_uri(httpretty.DELETE, '{0}/{1}'.format(endpoint_url, class_type),
                               body='This is the error.',
                               status=501)
        client = PMClient(endpoint_url)
        try:
            client.delete(class_type, params)
        except PMClientError as ex:
            self.assertTrue('501' in str(ex))
            self.assertTrue('This is the error.' in str(ex))

    @httpretty.activate
    def test_client_delete_unk_error(self):
        """Test the client response to an unknown error."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        params = {
            '_id': 127
        }
        httpretty.register_uri(httpretty.DELETE, '{0}/{1}'.format(endpoint_url, class_type),
                               body='This is the error.',
                               status=301)
        client = PMClient(endpoint_url)
        try:
            client.delete(class_type, params)
        except PMClientError as ex:
            self.assertTrue('301' in str(ex))
            self.assertTrue('This is the error.' in str(ex))

    @httpretty.activate
    def test_client_create_server_error(self):
        """Test the client response to an unknown error."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        response_body = {
            '_id': 127,
            'last_name': 'Doe',
            'first_name': 'John',
            'network_id': 'johndoe'
        }
        httpretty.register_uri(httpretty.PUT, '{0}/{1}'.format(endpoint_url, class_type),
                               body='This is the error.',
                               status=501)
        client = PMClient(endpoint_url)
        try:
            client.create(class_type, response_body)
        except PMClientError as ex:
            self.assertTrue('501' in str(ex))
            self.assertTrue('This is the error.' in str(ex))

    @httpretty.activate
    def test_client_create_unk_error(self):
        """Test the client response to an unknown error."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        response_body = {
            '_id': 127,
            'last_name': 'Doe',
            'first_name': 'John',
            'network_id': 'johndoe'
        }
        httpretty.register_uri(httpretty.PUT, '{0}/{1}'.format(endpoint_url, class_type),
                               body='This is the error.',
                               status=301)
        client = PMClient(endpoint_url)
        try:
            client.create(class_type, response_body)
        except PMClientError as ex:
            self.assertTrue('301' in str(ex))
            self.assertTrue('This is the error.' in str(ex))

    @httpretty.activate
    def test_client_create(self):
        """Test the client response to an unknown error."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        response_body = {
            '_id': 127,
            'last_name': 'Doe',
            'first_name': 'John',
            'network_id': 'johndoe'
        }
        httpretty.register_uri(
            httpretty.PUT, '{0}/{1}'.format(endpoint_url, class_type))
        client = PMClient(endpoint_url)
        response = client.create(class_type, response_body)
        self.assertTrue(response)
        chk_body = loads(httpretty.last_request().body.decode('UTF-8'))
        for key, value in response_body.items():
            self.assertEqual(chk_body[key], value)

    @httpretty.activate
    def test_client_update(self):
        """Test the client response to an unknown error."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        params = {
            '_id': 127
        }
        response_body = {
            '_id': 127,
            'last_name': 'Doe',
            'first_name': 'John',
            'network_id': 'johndoe'
        }
        httpretty.register_uri(
            httpretty.POST, '{0}/{1}'.format(endpoint_url, class_type))
        client = PMClient(endpoint_url)
        response = client.update(class_type, params, response_body)
        self.assertTrue(response)

    @httpretty.activate
    def test_client_update_not_found(self):
        """Test the client response to not finding things."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        params = {
            '_id': 127
        }
        response_body = {}
        post_body = {
            '_id': 127,
            'last_name': 'Doe',
            'first_name': 'John',
            'network_id': 'johndoe'
        }
        httpretty.register_uri(httpretty.POST, '{0}/{1}'.format(endpoint_url, class_type),
                               body=dumps(response_body),
                               content_type='application/json',
                               status=404)
        client = PMClient(endpoint_url)
        response = client.update(class_type, params, post_body)
        self.assertFalse(response)

    @httpretty.activate
    def test_client_update_server_error(self):
        """Test the client response to not finding things."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        params = {
            '_id': 127
        }
        post_body = {
            '_id': 127,
            'last_name': 'Doe',
            'first_name': 'John',
            'network_id': 'johndoe'
        }
        httpretty.register_uri(httpretty.POST, '{0}/{1}'.format(endpoint_url, class_type),
                               body=unicode_type('This is the error.'),
                               status=501)
        client = PMClient(endpoint_url)
        try:
            client.update(class_type, params, post_body)
        except PMClientError as ex:
            self.assertTrue('501' in str(ex))
            self.assertTrue('This is the error.' in str(ex))
            self.assertTrue('Internal Server Error' in str(ex))

    @httpretty.activate
    def test_client_update_unk_error(self):
        """Test the client response to not finding things."""
        endpoint_url = 'http://127.0.0.1:8080'
        class_type = 'users'
        params = {
            '_id': 127
        }
        post_body = {
            '_id': 127,
            'last_name': 'Doe',
            'first_name': 'John',
            'network_id': 'johndoe'
        }
        httpretty.register_uri(httpretty.POST, '{0}/{1}'.format(endpoint_url, class_type),
                               body='This is the error.',
                               status=301)
        client = PMClient(endpoint_url)
        try:
            client.update(class_type, params, post_body)
        except PMClientError as ex:
            self.assertTrue('301' in str(ex))
            self.assertTrue('This is the error.'in str(ex))
