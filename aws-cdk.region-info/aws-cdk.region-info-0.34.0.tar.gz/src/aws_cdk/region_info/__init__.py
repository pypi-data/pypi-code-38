import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/region-info", "0.34.0", __name__, "region-info@0.34.0.jsii.tgz")
class Default(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/region-info.Default"):
    """Provides default values for certain regional information points.

    Stability:
        experimental
    """
    @jsii.member(jsii_name="servicePrincipal")
    @classmethod
    def service_principal(cls, service: str, region: str, url_suffix: str) -> str:
        """Computes a "standard" AWS Service principal for a given service, region and suffix.

        This is useful for example when
        you need to compute a service principal name, but you do not have a synthesize-time region literal available (so
        all you have is ``{ "Ref": "AWS::Region" }``). This way you get the same defaulting behavior that is normally used
        for built-in data.

        Arguments:
            service: the name of the service (s3, s3.amazonaws.com, ...).
            region: the region in which the service principal is needed.
            urlSuffix: the URL suffix for the partition in which the region is located.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "servicePrincipal", [service, region, url_suffix])


class Fact(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/region-info.Fact"):
    """A database of regional information.

    Stability:
        experimental
    """
    @jsii.member(jsii_name="find")
    @classmethod
    def find(cls, region: str, name: str) -> typing.Optional[str]:
        """Retrieves a fact from this Fact database.

        Arguments:
            region: the name of the region (e.g: ``us-east-1``).
            name: the name of the fact being looked up (see the ``FactName`` class for details).

        Returns:
            the fact value if it is known, and ``undefined`` otherwise.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "find", [region, name])

    @jsii.member(jsii_name="register")
    @classmethod
    def register(cls, fact: "IFact", allow_replacing: typing.Optional[bool]=None) -> None:
        """Registers a new fact in this Fact database.

        Arguments:
            fact: the new fact to be registered.
            allowReplacing: whether new facts can replace existing facts or not.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "register", [fact, allow_replacing])

    @jsii.member(jsii_name="unregister")
    @classmethod
    def unregister(cls, region: str, name: str, value: typing.Optional[str]=None) -> None:
        """Removes a fact from the database.

        Arguments:
            region: the region for which the fact is to be removed.
            name: the name of the fact to remove.
            value: the value that should be removed (removal will fail if the value is specified, but does not match the current stored value).

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "unregister", [region, name, value])


class FactName(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/region-info.FactName"):
    """All standardized fact names.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(FactName, self, [])

    @jsii.member(jsii_name="servicePrincipal")
    @classmethod
    def service_principal(cls, service: str) -> str:
        """The name of the regional service principal for a given service.

        Arguments:
            service: the service name, either simple (e.g: ``s3``, ``codedeploy``) or qualified (e.g: ``s3.amazonaws.com``). The ``.amazonaws.com`` and ``.amazonaws.com.cn`` domains are stripped from service names, so they are canonicalized in that respect.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "servicePrincipal", [service])

    @classproperty
    @jsii.member(jsii_name="cdkMetadataResourceAvailable")
    def CDK_METADATA_RESOURCE_AVAILABLE(cls) -> str:
        """Whether the AWS::CDK::Metadata CloudFormation Resource is available in-region or not.

        The value is a boolean
        modelled as ``YES`` or ``NO``.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cdkMetadataResourceAvailable")

    @classproperty
    @jsii.member(jsii_name="domainSuffix")
    def DOMAIN_SUFFIX(cls) -> str:
        """The domain suffix for a region (e.g: 'amazonaws.com`).

        Stability:
            experimental
        """
        return jsii.sget(cls, "domainSuffix")

    @classproperty
    @jsii.member(jsii_name="partition")
    def PARTITION(cls) -> str:
        """The name of the partition for a region (e.g: 'aws', 'aws-cn', ...).

        Stability:
            experimental
        """
        return jsii.sget(cls, "partition")

    @classproperty
    @jsii.member(jsii_name="s3StaticWebsiteEndpoint")
    def S3_STATIC_WEBSITE_ENDPOINT(cls) -> str:
        """The endpoint used for hosting S3 static websites.

        Stability:
            experimental
        """
        return jsii.sget(cls, "s3StaticWebsiteEndpoint")


@jsii.interface(jsii_type="@aws-cdk/region-info.IFact")
class IFact(jsii.compat.Protocol):
    """A fact that can be registered about a particular region.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IFactProxy

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """The name of this fact.

        Standardized values are provided by the ``Facts`` class.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="region")
    def region(self) -> str:
        """The region for which this fact applies.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="value")
    def value(self) -> str:
        """The value of this fact.

        Stability:
            experimental
        """
        ...


class _IFactProxy():
    """A fact that can be registered about a particular region.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/region-info.IFact"
    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """The name of this fact.

        Standardized values are provided by the ``Facts`` class.

        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @property
    @jsii.member(jsii_name="region")
    def region(self) -> str:
        """The region for which this fact applies.

        Stability:
            experimental
        """
        return jsii.get(self, "region")

    @property
    @jsii.member(jsii_name="value")
    def value(self) -> str:
        """The value of this fact.

        Stability:
            experimental
        """
        return jsii.get(self, "value")


class RegionInfo(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/region-info.RegionInfo"):
    """Information pertaining to an AWS region.

    Stability:
        experimental
    """
    @jsii.member(jsii_name="get")
    @classmethod
    def get(cls, name: str) -> "RegionInfo":
        """Obtain region info for a given region name.

        Arguments:
            name: the name of the region (e.g: us-east-1).

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "get", [name])

    @jsii.member(jsii_name="servicePrincipal")
    def service_principal(self, service: str) -> typing.Optional[str]:
        """The name of the service principal for a given service in this region.

        Arguments:
            service: the service name (e.g: s3.amazonaws.com).

        Stability:
            experimental
        """
        return jsii.invoke(self, "servicePrincipal", [service])

    @property
    @jsii.member(jsii_name="cdkMetadataResourceAvailable")
    def cdk_metadata_resource_available(self) -> bool:
        """Whether the ``AWS::CDK::Metadata`` CloudFormation Resource is available in this region or not.

        Stability:
            experimental
        """
        return jsii.get(self, "cdkMetadataResourceAvailable")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @property
    @jsii.member(jsii_name="domainSuffix")
    def domain_suffix(self) -> typing.Optional[str]:
        """The domain name suffix (e.g: amazonaws.com) for this region.

        Stability:
            experimental
        """
        return jsii.get(self, "domainSuffix")

    @property
    @jsii.member(jsii_name="partition")
    def partition(self) -> typing.Optional[str]:
        """The name of the ARN partition for this region (e.g: aws).

        Stability:
            experimental
        """
        return jsii.get(self, "partition")

    @property
    @jsii.member(jsii_name="s3StaticWebsiteEndpoint")
    def s3_static_website_endpoint(self) -> typing.Optional[str]:
        """The endpoint used by S3 static website hosting in this region (e.g: s3-static-website-us-east-1.amazonaws.com).

        Stability:
            experimental
        """
        return jsii.get(self, "s3StaticWebsiteEndpoint")


__all__ = ["Default", "Fact", "FactName", "IFact", "RegionInfo", "__jsii_assembly__"]

publication.publish()
