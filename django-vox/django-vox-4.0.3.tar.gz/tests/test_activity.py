import json

import aspy
from django.test import Client, TestCase

import django_vox.models
import django_vox.settings
from tests import models

EXTRA = {"HTTP_ACCEPT": "application/activity+json"}


class WebTests(TestCase):
    """Test the walkthrough in the documentation"""

    fixtures = ["test"]

    @staticmethod
    def test_bad_requests():
        client = Client()
        get_list = (
            ("/~1/inbox", 200, "Sanity check failed"),
            ("/~404/", 404, "Didn't return 404 on bad endpoint"),
            ("/~404/inbox", 404, "Didn't return 404 on bad inbox"),
            ("/~2/inbox", 403, "Didn't return 403 on other user's inbox"),
            ("/~1/outbox", 405, "Didn't return 405 on getting outbox"),
        )
        post_list = (
            ("/~404/outbox", 404, "Didn't return 404 on bad outbox"),
            ("/~2/outbox", 403, "Didn't return 403 on other user's outbox"),
            ("/~1/inbox", 405, "Didn't return 405 on getting inbox"),
        )
        response = client.post(
            "/admin/login/", {"username": "author@example.org", "password": "password"}
        )
        assert 302 == response.status_code, "login failed"
        response = client.get("/~1/inbox", **EXTRA)
        for url, status, info in get_list:
            response = client.get(url, **EXTRA)
            assert status == response.status_code, info
        for url, status, info in post_list:
            response = client.post(url, {}, **EXTRA)
            assert status == response.status_code, info
        # test and empty endpoint
        response = client.get("/~1/followers", **EXTRA)
        assert 200 == response.status_code
        data = json.loads(response.content)
        assert "Collection" == data["type"]
        assert "items" not in data

    @staticmethod
    def test_actor_page():
        client = Client()
        response = client.get("/~1/", **EXTRA)
        assert 200 == response.status_code
        assert "application/activity+json" == response["Content-Type"]
        json_obj = json.loads(response.content)
        assert "Person" == json_obj["type"]
        assert "http://127.0.0.1:8000/~1/" == json_obj["id"]

    @staticmethod
    def test_article_add():
        # sanity check
        assert django_vox.models.InboxItem.objects.count() == 0
        article = models.Article.objects.get(pk="too_many")
        subscriber = models.Subscriber.objects.get(id=1)
        author_subscriber = models.Subscriber.objects.get(id=2)
        # first we create an article as the author user
        models.Comment.objects.create(
            article=article, poster=subscriber, content="First Post!11"
        )
        models.Comment.objects.create(
            article=article,
            poster=author_subscriber,
            content="This is why we can't have nice things",
        )
        # now two notification should have been fired, check the
        # inbox items
        assert 2 == django_vox.models.InboxItem.objects.count()
        # now, let's check the results of the inbox endpoint
        client = Client()

        # fist we have to authenticate
        response = client.post(
            "/admin/login/", {"username": "author@example.org", "password": "password"}
        )
        assert 302 == response.status_code, "login failed"
        response = client.get("/~1/inbox", **EXTRA)
        assert 200 == response.status_code
        assert "application/activity+json" == response["Content-Type"]
        json_obj = json.loads(response.content)
        assert "OrderedCollection" == json_obj["type"]
        items = json_obj["items"]
        assert 2 == len(items)
        # in make sure this is in descending order
        assert "http://127.0.0.1:8000/too_many/#comment-1" == items[1]["object"]["id"]
        assert "First Post!11" == items[1]["object"]["content"]
        assert "Note" == items[1]["object"]["name"]
        assert "http://127.0.0.1:8000/too_many/#comment-2" == items[0]["object"]["id"]
        assert "Author Subscriber" == items[0]["actor"]["name"]

    @staticmethod
    def test_activity_read():
        # sanity check
        assert django_vox.models.InboxItem.objects.count() == 0
        article = models.Article.objects.get(pk="too_many")
        subscriber = models.Subscriber.objects.get(id=1)
        # first we create an article as the author user
        models.Comment.objects.create(
            article=article, poster=subscriber, content="read me"
        )
        # now one notification should have been fired, check the
        # inbox items
        assert 1 == django_vox.models.InboxItem.objects.count()
        # now we'll check the activity
        client = Client()
        response = client.post(
            "/admin/login/", {"username": "author@example.org", "password": "password"}
        )
        assert 302 == response.status_code, "login failed"
        # make sure inbox looks normal
        response = client.get("/~1/inbox", **EXTRA)
        assert 200 == response.status_code
        assert "application/activity+json" == response["Content-Type"]
        json_obj = json.loads(response.content)
        assert "OrderedCollection" == json_obj["type"]
        items = json_obj["items"]
        assert 1 == len(items)
        item_id = items[0]["id"]
        # check db
        inbox = django_vox.models.InboxItem.objects.all()
        assert 1 == len(inbox)
        assert inbox[0].read_at is None
        # now mark the message as read
        activity = aspy.Read(object=item_id)
        response = client.post("/~1/outbox", activity.to_dict(), **EXTRA)
        assert 200 == response.status_code
        # now we should have one read item
        inbox = django_vox.models.InboxItem.objects.all()
        assert 1 == len(inbox)
        assert inbox[0].read_at is not None
