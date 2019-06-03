from uuid import UUID
from uuid import uuid4
from base64 import urlsafe_b64decode
from base64 import urlsafe_b64encode


def uuid_to_slug(uuid):
    return urlsafe_b64encode(uuid.bytes).rstrip(b'=').decode('ascii')


def slug_to_uuid(slug):
    return UUID(bytes=urlsafe_b64decode(slug + '=='))


class GUID():
    def __init__(self):
        self._uuid = uuid4()
        self._slug = uuid_to_slug(self._uuid)

    @property
    def uuid(self):
        return str(self._uuid)

    @property
    def slug(self):
        return self._slug

    def to_uuid(self):
        return self._uuid

    def __repr__(self):
        return "{'uuid': '%s', 'slug': '%s'}" % (self._uuid, self._slug)

    def __str__(self):
        return self._slug
