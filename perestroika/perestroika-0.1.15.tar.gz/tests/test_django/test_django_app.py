import django
django.setup()

from json import dumps

from django.contrib.auth.models import User
from django.test import TestCase

from perestroika.exceptions import BadRequest
from perestroika.utils import dict_to_multi_dict


class DjangoTest(TestCase):
    def make_post(self, url, data):
        return self.client.post(url, dumps(data), content_type='application/json')

    def make_put(self, url, data):
        return self.client.put(url, dumps(data), content_type='application/json')

    def make_empty_post(self, url):
        return self.client.post(url, content_type='application/json')

    def make_get(self, url, data):
        data = dict_to_multi_dict(data)
        return self.client.get(url, data, content_type='application/json')

    def test_allowed_methods(self):
        _response = self.make_post("/test/empty/", {})
        assert _response.status_code == 405

    def test_empty_get(self):
        User(username="first").save()

        assert User.objects.count() == 1

        _response = self.make_get("/test/full/", {})
        assert _response.status_code == 200
        assert _response.json() == {
            'items': [{'username': "first"}],
            'status_code': 200,
            'total': 1
        }

        User(username="second").save()

        assert User.objects.count() == 2

        _response = self.make_get("/test/full/", {})
        assert _response.status_code == 200
        assert _response.json() == {
            'items': [{'username': "first"}, {"username": "second"}],
            'status_code': 200,
            'total': 2
        }

    def test_json_validation_no_items(self):
        with self.assertRaises(BadRequest):
            _response = self.make_empty_post("/test/full/")

    def test_post(self):
        assert User.objects.count() == 0

        _response = self.make_post("/test/full/", {'items': [{'username': "third"}]})
        assert _response.status_code == 201
        assert _response.json() == {
            'status_code': 201,
            'created': 1
        }

    def test_put(self):
        assert User.objects.count() == 0

        _response = self.make_post("/test/full/", {'items': [{'username': "third"}]})
        assert User.objects.count() == 1

        _response = self.make_put("/test/full/", {'items': [{'username': "fourth"}]})
        assert User.objects.count() == 1

        assert User.objects.all().first().username == "fourth"

    def test_admin(self):
        _response = self.make_get("/admin/", {})
        assert _response.status_code in [200, 302]

    def test_filter_get(self):
        User(username="first").save()
        User(username="second").save()
        User(username="third").save()

        assert User.objects.count() == 3

        _response = self.make_get("/test/full/", {'filter.username__in': 'first'})
        assert _response.status_code == 200

        assert _response.json() == {
            'items': [{'username': "first"}],
            'filter': {'username__in': ['first']},
            'status_code': 200,
            'total': 1
        }

    def test_exclude_get(self):
        User(username="first").save()
        User(username="second").save()
        User(username="third").save()

        assert User.objects.count() == 3

        _response = self.make_get("/test/full/", {'exclude.username__in': 'first'})
        assert _response.status_code == 200

        assert _response.json() == {
            'items': [{'username': "second"}, {'username': "third"}],
            'exclude': {'username__in': ['first']},
            'status_code': 200,
            'total': 2
        }

    def test_filter_put(self):
        User(username="first").save()
        User(username="second").save()
        User(username="third").save()

        assert User.objects.count() == 3

        _response = self.make_put("/test/full/", {'items': [{'username': 'fourth'}], 'filter.username': 'first'})
        assert _response.json() == {
            'filter': {'username': 'first'},
            'updated': 1,
            'status_code': 200,
        }
        assert _response.status_code == 200

        _response = self.make_get("/test/full/", {})
        assert _response.status_code == 200

        assert _response.json() == {
            'items': [{'username': "fourth"}, {'username': "second"}, {'username': "third"}],
            'status_code': 200,
            'total': 3
        }

    def test_exclude_put(self):
        User(username="first").save()
        User(username="second").save()
        User(username="third").save()

        assert User.objects.count() == 3

        _response = self.make_put("/test/full/", {'items': [{'username': 'fourth'}],
                                                  'exclude.username__in': ['first', 'second']})
        assert _response.json() == {
            'exclude': {'username__in': ['first', 'second']},
            'updated': 1,
            'status_code': 200,
        }
        assert _response.status_code == 200

        _response = self.make_get("/test/full/", {})
        assert _response.status_code == 200

        assert _response.json() == {
            'items': [{'username': "first"}, {'username': "second"}, {'username': "fourth"}],
            'status_code': 200,
            'total': 3
        }
