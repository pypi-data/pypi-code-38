"""
http://flask.pocoo.org/docs/1.0/testing/
https://cloud.google.com/appengine/docs/standard/python/getting-started/python-standard-env
"""
import unittest
try:  # pragma: no cover
    from urllib import urlencode
    from urlparse import urlparse
except ImportError:  # pragma: no cover
    from urllib.parse import urlparse, urlencode  # pylint: disable=ungrouped-imports


class RequestFactory:  # pylint: disable=too-few-public-methods
    """
    requests generator
    """
    def __init__(self, app):
        self.app = app

    def post(self, url, data='', content_type='application/octet-stream'):
        """
        post requests tests
        """
        return self.app.test_request_context(url, data=data, method='POST', content_type=content_type)


class TestFlask(unittest.TestCase):
    """
    Flask apps tester
    """
    def setUp(self, app):  # pylint: disable=arguments-differ
        unittest.TestCase.setUp(self)
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.factory = RequestFactory(self.app)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def get_url(self, view_name, **kwargs):
        """
        generate url for view in app test context
        """
        with self.app.test_request_context():
            from flask import url_for
            url = url_for(view_name, **kwargs)

        return url

    def guest_view(self, url, return_code=200, follow_redirects=False):
        """
        generic get request
        """
        response = self.client.get(url, follow_redirects=follow_redirects)

        self.assertEqual(
          response.status_code,
          return_code,
          "guest_view {}: {} -> {}".format(return_code, url, response.status_code)
        )
        return response

    def simple_view(self, view_name, return_code=200, follow=False, get_param=None):
        """
        simple get request
        """
        url = self.get_url(view_name)
        if get_param:
            url = url + "?" + urlencode(get_param)
        return self.guest_view(url, return_code=return_code, follow_redirects=follow)

    def param_view(
      self, view_name, params, return_code=200, follow=False, get_param=None
    ):  # pylint: disable=too-many-arguments
        """
        get request with parameters
        """
        url = self.get_url(view_name, **params)
        if get_param:
            url = url + "?" + urlencode(get_param)
        return self.guest_view(url, return_code=return_code, follow_redirects=follow)

    def simple_post(self, view_name, post_dict, follow=True, content_type=None):
        """
        simple post request
        """
        url = self.get_url(view_name)
        return self.client.post(url, data=post_dict, follow_redirects=follow, content_type=content_type)

    def param_post(
      self, view_name, params, post_dict, follow=True, get_param=None, content_type=None
    ):  # pylint: disable=too-many-arguments
        """
        post request with parameters
        """
        url = self.get_url(view_name, **params)
        if get_param:
            url = url + "?" + urlencode(get_param)
        return self.client.post(url, data=post_dict, follow_redirects=follow, content_type=content_type)

    def final_url(self, response):
        """
        return final url after redirect
        """
        self.assertEqual(response.status_code, 302)
        return urlparse(response.location).path
