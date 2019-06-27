# -*- coding: utf-8 -*-

from .base import Service


class STS(Service):
    service_name = 'sts'

    def __init__(self, session=None):
        super().__init__(session)

    @classmethod
    def as_assume_role(cls,
                       aws_access_key_id, aws_secret_access_key,
                       role_arn, session_name=None):
        raise AttributeError

    def assume_role(self, role_arn, session_name=None):
        if session_name is None:
            from datetime import datetime
            session_name = str(datetime.utcnow().timestamp())

        res = self.client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )

        return res
