from datetime import datetime

from .utils import get_user_group_model
from django.conf import settings
from django.contrib.auth import get_user_model
from hyperstools.mq.lib import Queue

listenHacMq = settings.HAC_LISTEN_MQ
publishHacMq = settings.HAC_PUBLISH_MQ
User = get_user_model()
UserGroup = get_user_group_model()


def callback(body):
    HacUtility(body).run()


class HacUtility(object):
    service = None
    domain = None

    def __init__(self, body):
        self.code = 200000
        self.uuid = body["uuid"]
        self.method = body["method"]
        self.resource = body["resource"]
        self.data = body["body"]["data"]
        self.name = self.data.get("name", None)
        self.email = self.data.get("email", None)
        self.group = self.data.get("group", None)
        self.role = self.data.get("role", None)
        self.creator = self.data.get("creator", None)
        self.groupId = self.data.get("groupId", None)

    def run(self):
        try:
            self.resourceHandler()
        except Exception:
            self.code = 200001
        self.publishReturn()

    def publishReturn(self):
        body = {
            "uuid": self.uuid,
            "service": self.service,
            "domain": self.domain,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "method": self.method,
            "resource": self.resource,
            "body": {"code": self.code},
        }
        body["body"].update(result=self.data)
        with Queue(publishHacMq) as queue:
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
