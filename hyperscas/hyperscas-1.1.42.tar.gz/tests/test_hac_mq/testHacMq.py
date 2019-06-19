import copy
import datetime
from django.test import TestCase
from unittest import mock
import pytest
from cas.mq import AuthMQ
from django.contrib.auth import get_user_model
from cas.utils import get_user_group_model
from tests.test_hac_mq.factories import UserFactory, UserGroupFactory


User = get_user_model()
UserGroup = get_user_group_model()

testData = {
    "uuid": "f66d5bc4-5264-4333-ba6a-19ea97b6420f",
    "service": "dmp",
    "domain": "https://dmp.hypers.com.cn",
    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "method": "",
    "resource": "",
    "body": {"data": {}},
}


@pytest.mark.django_db
class HacMqUserTestCase(TestCase):
    def setUp(self) -> None:
        self._testData = copy.deepcopy(testData)
        self._testData["resource"] = "/users"
        self._testData["body"]["data"] = {
            "authId": 6106,
            "name": "testMQ",
            "email": "test@hypers.com",
            "userId": 970,
            "group": "SaaS",
            "role": "MEMBER",
            "creator": "xxx",
            "businesses": [1],
        }

    @mock.patch("cas.mq.AuthMQ.publish")
    def testPost(self, *args):
        body = self._testData
        body["method"] = "POS"
        hac = AuthMQ(body)
        hac.run()
        self.assertEqual(hac.code, 200002)
        uuid = body.pop("uuid")
        hac = AuthMQ(body)
        hac.run()
        self.assertEqual(hac.code, 200002)
        body["method"] = "POST"
        body["uuid"] = uuid
        hac = AuthMQ(body)
        hac.run()
        user = User.objects.first()
        data = body["body"]["data"]
        self.assertEqual(user.username, data["name"])
        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.role, data["role"])
        self.assertEqual(user.is_active, 1)

    @mock.patch("cas.mq.AuthMQ.publish")
    def testPatch(self, *args):
        body = self._testData
        body["method"] = "PATCH"
        data = body["body"]["data"]
        UserFactory(email=data["email"])
        hac = AuthMQ(body)
        hac.run()
        user = User.objects.first()
        self.assertEqual(user.username, data["name"])
        self.assertEqual(user.role, data["role"])

    def testPut(self):
        self.testPatch()

    @mock.patch("cas.mq.AuthMQ.publish")
    def testDelete(self, *args):
        body = self._testData
        body["method"] = "DELETE"
        data = body["body"]["data"]
        UserFactory(email=data["email"], is_active=1)
        hac = AuthMQ(body)
        hac.run()
        user = User.objects.first()
        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.is_active, False)


@pytest.mark.django_db
class HacMqUserGroupTestCase(TestCase):
    def setUp(self) -> None:
        self._testData = copy.deepcopy(testData)
        self._testData["resource"] = "/group"
        self._testData["body"]["data"] = {
            "authId": 1301,
            "name": "testGroupMQ",
            "groupId": 855,
            "creator": "test@hypers.com",
        }

    @mock.patch("cas.mq.AuthMQ.publish")
    def testPost(self, *args):
        UserFactory(email=self._testData["body"]["data"]["creator"])
        body = self._testData
        body["method"] = "POST"
        hac = AuthMQ(body)
        hac.run()
        self.assertEqual(hac.code, 200000)
        self.assertEqual(hac.method, body["method"].upper())
        usergroup = UserGroup.objects.all().first()
        user = UserGroup.objects.all().first()
        self.assertEqual(usergroup.creator_id, user.id)
        self.assertEqual(usergroup.group_id, body["body"]["data"]["groupId"])
        self.assertEqual(usergroup.name, body["body"]["data"]["name"])
        self.assertEqual(usergroup.status, "ACTIVE")

    def testPut(self):
        self.testPatch()

    @mock.patch("cas.mq.AuthMQ.publish")
    def testPatch(self, *args):
        body = self._testData
        body["method"] = "PATCH"
        UserGroupFactory(
            name="oldName", group_id=body["body"]["data"]["groupId"]
        )
        hac = AuthMQ(body)
        hac.run()
        usergroup = UserGroup.objects.first()
        self.assertEqual(hac.code, 200000)
        self.assertEqual(usergroup.group_id, body["body"]["data"]["groupId"])
        self.assertEqual(usergroup.name, body["body"]["data"]["name"])

    @mock.patch("cas.mq.AuthMQ.publish")
    def testDelete(self, *args):
        body = self._testData
        UserGroupFactory(name=body["body"]["data"]["name"])
        body["method"] = "DELETE"
        hac = AuthMQ(body)
        hac.run()
        usergroup = UserGroup.objects.first()
        self.assertEqual(hac.code, 200000)
        self.assertEqual(usergroup.status, "PAUSED")
