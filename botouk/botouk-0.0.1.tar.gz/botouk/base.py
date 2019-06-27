# -*- coding: utf-8 -*-
import boto3
from boto3 import Session as BaseSession


class Session(BaseSession):
    def __init__(self, expiration=None, **kwargs):
        super().__init__(**kwargs)
        self.expiration = expiration

    @classmethod
    def from_profile_name(cls, profile_name):
        return cls(profile_name=profile_name)

    @classmethod
    def from_access_key(cls, aws_access_key_id, aws_secret_access_key):
        return cls(aws_access_key_id=aws_access_key_id,
                   aws_secret_access_key=aws_secret_access_key)

    @classmethod
    def from_session_token(cls,
                           aws_access_key_id, aws_secret_access_key,
                           aws_session_token, expiration=None):
        return cls(aws_access_key_id=aws_access_key_id,
                   aws_secret_access_key=aws_secret_access_key,
                   aws_session_token=aws_session_token,
                   expiration=expiration)

    @classmethod
    def as_assume_role(cls,
                       aws_access_key_id, aws_secret_access_key,
                       role_arn, session_name=None):
        from botouk.sts import STS

        sts = STS.from_access_key(aws_access_key_id, aws_secret_access_key)
        res = sts.assume_role(role_arn, session_name)

        key = res['Credentials']['AccessKeyId']
        sec = res['Credentials']['SecretAccessKey']
        token = res['Credentials']['SessionToken']
        expiration = res['Credentials']['Expiration']

        return cls.from_session_token(aws_access_key_id=key,
                                      aws_secret_access_key=sec,
                                      aws_session_token=token,
                                      expiration=expiration)


class Service:
    service_name = None

    def __init__(self, session=None):
        self.session = session or boto3
        self._client = None
        self.expiration = None
        if session and hasattr(session, 'expiration'):
            self.expiration = session.expiration

    @property
    def client(self):
        if self._client is None:
            self._client = self.session.client(self.service_name)
        return self._client

    @classmethod
    def from_profile_name(cls, profile_name):
        return cls(Session.
                   from_profile_name(profile_name=profile_name))

    @classmethod
    def from_access_key(cls, aws_access_key_id, aws_secret_access_key):
        return cls(Session.
                   from_access_key(aws_access_key_id, aws_secret_access_key))

    @classmethod
    def from_session_token(cls,
                           aws_access_key_id, aws_secret_access_key,
                           aws_session_token, expiration=None):
        return cls(Session.
                   from_session_token(aws_access_key_id,
                                      aws_secret_access_key,
                                      aws_session_token,
                                      expiration))

    @classmethod
    def as_assume_role(cls,
                       aws_access_key_id, aws_secret_access_key,
                       role_arn, session_name=None):
        return cls(Session.
                   as_assume_role(aws_access_key_id, aws_secret_access_key,
                                  role_arn, session_name))


class ResourceMixIn:
    def __init__(self):
        self._resource = None

    @property
    def resource(self):
        if not hasattr(self, '_resource'):
            setattr(self, '_resource', None)

        if self._resource is None:
            self._resource = self.session.resource(self.service_name)
        return self._resource
