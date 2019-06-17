from troposphere import (
    Tags,
    Ref,
    Sub
)
from troposphere.iam import (
    Policy, Role
)
from ozone.tags import IamRoleTags

from datetime import date
import hashlib

def role_trust_policy(service_name, require_mfa=False, external_id=None):
    """
    """
    statement = {
        "Effect": "Allow",
        "Principal": {
            "Service": [
                Sub(f'{service_name}.${{AWS::URLSuffix}}')
            ]
        },
        "Action": [ "sts:AssumeRole" ]
    }
    if require_mfa or external_id:
        statement['Condition'] = {}
        if require_mfa:
            statement['Condition']['Bool'] = {
                "aws:MultiFactorAuthPresent": "true"
            }
        if external_id is not None:
            statement['Condition']['StringEquals'] = {
                "sts:ExternalId": external_id
            }
    policy_doc = {
        "Version" : "2012-10-17",
        "Statement": [
            statement
        ]
    }
    return policy_doc


def pass_policy(to_services, name=None, resource=None):
    services = []
    if not isinstance(to_services, list):
        raise TypeError('services must be of type', list)
    for service in to_services:
        if service.endswith('.com') or service.endswith('.com.cn'):
            services.append(service)
        else:
            services.append(Sub(f'{service}.${{URLSuffix}}'))
    statement = {
        "Action": [
            "iam:PassRole"
        ],
        "Resource": "*",
        "Effect": "Allow",
        "Condition": {
            "StringEqualsIfExists": {
                "iam:PassedToService": services
            }
        }
    }
    policy = Policy(
        PolicyName='AllowPassRoleTo'.join('', to_services),
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                statement
            ]
        }
    )
    return policy


class IamRole(Role, object):
    """
    Simple Class to initialize a role and add access policies to it
    """


    def __init__(self, title, services, mfa=False, external_id=None, tags_function=None, **kwargs):
        """
        Args:
          services: string / list of services to allow to assume the role
          kwargs:
        """
        super().__init__(
            title,
            AssumeRolePolicyDocument=role_trust_policy(services, mfa, external_id)
        )
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

