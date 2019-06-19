from datetime import datetime

from .utils import get_user_group_model
from django.conf import settings
from django.contrib.auth import get_user_model
from hyperstools.mq.lib import Queue

SERVICE = settings.SERVICE
DOMAIN = settings.DOMAIN
PUBLISH_QUEUE = settings.HAC_PUBLISH_MQ
User = get_user_model()
UserGroup = get_user_group_model()


def callback(body):
    """
    监听到hac消息后的回调函数
    :param body: hac的消息体
    :return:
    """
    AuthMQ(body).run()


class AuthMQ(object):
    service = SERVICE
    domain = DOMAIN

    def __init__(self, body):
        self.body = body
        self.errField = None
        try:
            self.uuid = body["uuid"]
            self.method = body["method"]
            self.resource = body["resource"]
            self.data = body["body"]["data"]
            self.name = self.data.get("name", None)
            self.email = self.data["email"]
            self.group = self.data.get("group", None)
            self.role = self.data.get("role", None)
            self.creator = self.data.get("creator", None)
            self.groupId = self.data.get("groupId", None)
            self.code = 200000
        except KeyError as e:
            self.code = 200002
            e = str(e).replace("'", "")
            self.errField = {e: {
                "code": 200002,
                "massage": f"{e} is required"
            }}

    def run(self):
        try:
            self.resourceHandler()
        except AttributeError:
            self.code = 200002
            self.errField = self.errField or {"method": {"code": 200002, "massage": f"{self.method} is unsupported"}}
        except Exception:
            self.code = 200001
        self.publish()

    def publish(self):
        body = self.body
        if self.code == 200000:
            #  监听到的body没有出现字段错误, 去掉body["body"]中data, 加上code和result
            body["body"].pop("data")
            body["body"].update({
                "code": self.code,
                "result": self.data,
            })
        else:
            #  监听到的body出现字段错误，body["body"]加上code和result以及错误字段及信息，
            body["body"].update({
                "code": self.code,
                "result": "",
                "fields": self.errField
            })

        with Queue(PUBLISH_QUEUE) as queue:
            queue.publish(body)

    def resourceHandler(self):
        if self.resource.endswith("users"):
            self.code = getattr(UserResource(), self.method.lower())(self)
        elif self.resource.endswith("group"):
            self.code = getattr(UserGroupResource(), self.method.lower())(self)


class UserResource(object):

    def __init__(self):
        self.resultCode = 200000

    def get(self):
        pass

    def post(self, hac):
        queryset = User.objects.filter(email=hac.email)
        user = queryset.exists() and queryset.first() or User()
        user.email = hac.email
        user.username = hac.name
        user.role = hac.role
        user.is_active = 1
        if hac.group:
            group, created = UserGroup.objects.get_or_create(name=hac.group)
            user.usergroup = group

        setParamsExceptHac = getattr(user, "setParamsExceptHac", None)
        if setParamsExceptHac:
            setParamsExceptHac()  # 如果app的User model有除hac消息之外的字段，app须实现此接口
        user.save()
        return self.resultCode

    def put(self, hac):
        return self.patch(hac)

    def patch(self, hac):
        try:
            userInstance = User.objects.filter(email=hac.email).first()
            userInstance.username = hac.name
            userInstance.role = hac.role
            userInstance.save()
        except Exception:
            self.resultCode = 200404
        finally:
            return self.resultCode

    def delete(self, hac):
        try:
            userInstance = User.objects.filter(email=hac.email).first()
            userInstance.is_active = 0
            userInstance.save()
        except Exception:
            self.resultCode = 200404
        finally:
            return self.resultCode


class UserGroupResource(object):
    def __init__(self):
        self.resultCode = 200000

    def get(self):
        pass

    def post(self, hac):
        creator = User.objects.filter(email=hac.creator)
        group = UserGroup.objects.filter(name=hac.name)
        group = group and group[0] or UserGroup(name=hac.name)
        group.group_id = hac.groupId
        if creator:
            group.creator_id = creator[0].id
        group.status = "ACTIVE"
        setParamsExceptHac = getattr(group, "setParamsExceptHac", None)
        if setParamsExceptHac:
            setParamsExceptHac()  # 如果app的UserGroup model有除hac消息之外的字段，app须实现此接口
        group.save()
        return self.resultCode

    def put(self, hac):
        return self.patch(hac)

    def patch(self, hac):
        try:
            group = UserGroup.objects.get(group_id=hac.groupId)
            hac.name and setattr(group, "name", hac.name)
            group.save()
        except UserGroup.DoesNotExist:
            self.resultCode = 200404
        finally:
            return self.resultCode

    def delete(self, hac):
        try:
            group = UserGroup.objects.get(name=hac.name)
            group.status = "PAUSED"
            group.save()
        except UserGroup.DoesNotExist:
            self.resultCode = 200404
        finally:
            return self.resultCode
