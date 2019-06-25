import pytest

from parameterized import parameterized, param
from rest_framework.test import APIClient, APITestCase

"""Tests for `paraer` package."""
YN_CHOICES = ["y", "n"]


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


@pytest.fixture
def params_combination():
    return dict(windows=windows, windows1=windows1)


asdf = params_combination


class HomeViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/home"

    def test_get_name_blank(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 422)

    def test_get_name_ok(self):
        response = self.client.get(self.url, data={"name": "name"})
        self.assertEqual(response.status_code, 200)

    def test_get_identify_error(self):
        response = self.client.get(self.url, data={"name": "name", "identify": "a"})
        self.assertEqual(response.status_code, 422)

    @parameterized.expand(
        [param(asd='asd', efg='efg')]
    )
    def test_params_combination(self, *argv, **kwargs):
        import ipdb; ipdb.set_trace(context=30)
        response = self.client.get(self.url)
