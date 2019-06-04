"""Raw representations of every data type in the AWS ElasticLoadBalancing service.

See Also:
    `AWS developer guide for ElasticLoadBalancing
    <https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/index.html>`_

This file is automatically generated, and should not be directly edited.
"""

from attr import attrib
from attr import attrs

from ..core import ATTRSCONFIG
from ..core import Resource
from ..core import ResourceProperties
from ..core import create_object_converter

__all__ = ["LoadBalancer", "LoadBalancerProperties"]


@attrs(**ATTRSCONFIG)
class LoadBalancerProperties(ResourceProperties):
    AccessLoggingPolicy = attrib(default=None)
    AppCookieStickinessPolicy = attrib(default=None)
    AvailabilityZones = attrib(default=None)
    ConnectionDrainingPolicy = attrib(default=None)
    ConnectionSettings = attrib(default=None)
    CrossZone = attrib(default=None)
    HealthCheck = attrib(default=None)
    Instances = attrib(default=None)
    LBCookieStickinessPolicy = attrib(default=None)
    Listeners = attrib(default=None)
    LoadBalancerName = attrib(default=None)
    Policies = attrib(default=None)
    Scheme = attrib(default=None)
    SecurityGroups = attrib(default=None)
    Subnets = attrib(default=None)
    Tags = attrib(default=None)


@attrs(**ATTRSCONFIG)
class LoadBalancer(Resource):
    """A Load Balancer for ElasticLoadBalancing.

    See Also:
        `AWS Cloud Formation documentation for LoadBalancer
        <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html>`_
    """

    RESOURCE_TYPE = "AWS::ElasticLoadBalancing::LoadBalancer"

    Properties: LoadBalancerProperties = attrib(
        factory=LoadBalancerProperties,
        converter=create_object_converter(LoadBalancerProperties),
    )
