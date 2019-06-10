import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_cloudformation
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_route53
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-certificatemanager", "0.34.0", __name__, "aws-certificatemanager@0.34.0.jsii.tgz")
@jsii.data_type_optionals(jsii_struct_bases=[])
class _CertificateProps(jsii.compat.TypedDict, total=False):
    subjectAlternativeNames: typing.List[str]
    """Alternative domain names on your certificate.

    Use this to register alternative domain names that represent the same site.

    Default:
        - No additional FQDNs will be included as alternative domain names.

    Stability:
        experimental
    """
    validationDomains: typing.Mapping[str,str]
    """What validation domain to use for every requested domain.

    Has to be a superdomain of the requested domain.

    Default:
        - Apex domain is used for every domain that's not overridden.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-certificatemanager.CertificateProps", jsii_struct_bases=[_CertificateProps])
class CertificateProps(_CertificateProps):
    """Properties for your certificate.

    Stability:
        experimental
    """
    domainName: str
    """Fully-qualified domain name to request a certificate for.

    May contain wildcards, such as ``*.domain.com``.

    Stability:
        experimental
    """

class CfnCertificate(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-certificatemanager.CfnCertificate"):
    """A CloudFormation ``AWS::CertificateManager::Certificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CertificateManager::Certificate
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, domain_name: str, domain_validation_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union["DomainValidationOptionProperty", aws_cdk.cdk.Token]]]]]=None, subject_alternative_names: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, validation_method: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::CertificateManager::Certificate``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            domainName: ``AWS::CertificateManager::Certificate.DomainName``.
            domainValidationOptions: ``AWS::CertificateManager::Certificate.DomainValidationOptions``.
            subjectAlternativeNames: ``AWS::CertificateManager::Certificate.SubjectAlternativeNames``.
            tags: ``AWS::CertificateManager::Certificate.Tags``.
            validationMethod: ``AWS::CertificateManager::Certificate.ValidationMethod``.

        Stability:
            experimental
        """
        props: CfnCertificateProps = {"domainName": domain_name}

        if domain_validation_options is not None:
            props["domainValidationOptions"] = domain_validation_options

        if subject_alternative_names is not None:
            props["subjectAlternativeNames"] = subject_alternative_names

        if tags is not None:
            props["tags"] = tags

        if validation_method is not None:
            props["validationMethod"] = validation_method

        jsii.create(CfnCertificate, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, properties: typing.Any) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            properties: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [properties])

    @classproperty
    @jsii.member(jsii_name="resourceTypeName")
    def RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "resourceTypeName")

    @property
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "certificateArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnCertificateProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """The ``TagManager`` handles setting, removing and formatting tags.

        Tags should be managed either passing them as properties during
        initiation or by calling methods on this object. If both techniques are
        used only the tags from the TagManager will be used. ``Tag`` (aspect)
        will use the manager.

        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @jsii.data_type(jsii_type="@aws-cdk/aws-certificatemanager.CfnCertificate.DomainValidationOptionProperty", jsii_struct_bases=[])
    class DomainValidationOptionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-certificatemanager-certificate-domainvalidationoption.html
        Stability:
            experimental
        """
        domainName: str
        """``CfnCertificate.DomainValidationOptionProperty.DomainName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-certificatemanager-certificate-domainvalidationoption.html#cfn-certificatemanager-certificate-domainvalidationoptions-domainname
        Stability:
            experimental
        """

        validationDomain: str
        """``CfnCertificate.DomainValidationOptionProperty.ValidationDomain``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-certificatemanager-certificate-domainvalidationoption.html#cfn-certificatemanager-certificate-domainvalidationoption-validationdomain
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnCertificateProps(jsii.compat.TypedDict, total=False):
    domainValidationOptions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["CfnCertificate.DomainValidationOptionProperty", aws_cdk.cdk.Token]]]
    """``AWS::CertificateManager::Certificate.DomainValidationOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html#cfn-certificatemanager-certificate-domainvalidationoptions
    Stability:
        experimental
    """
    subjectAlternativeNames: typing.List[str]
    """``AWS::CertificateManager::Certificate.SubjectAlternativeNames``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html#cfn-certificatemanager-certificate-subjectalternativenames
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::CertificateManager::Certificate.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html#cfn-certificatemanager-certificate-tags
    Stability:
        experimental
    """
    validationMethod: str
    """``AWS::CertificateManager::Certificate.ValidationMethod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html#cfn-certificatemanager-certificate-validationmethod
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-certificatemanager.CfnCertificateProps", jsii_struct_bases=[_CfnCertificateProps])
class CfnCertificateProps(_CfnCertificateProps):
    """Properties for defining a ``AWS::CertificateManager::Certificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html
    Stability:
        experimental
    """
    domainName: str
    """``AWS::CertificateManager::Certificate.DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html#cfn-certificatemanager-certificate-domainname
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[CertificateProps])
class _DnsValidatedCertificateProps(CertificateProps, jsii.compat.TypedDict, total=False):
    region: str
    """AWS region that will host the certificate.

    This is needed especially
    for certificates used for CloudFront distributions, which require the region
    to be us-east-1.

    Default:
        the region the stack is deployed in.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-certificatemanager.DnsValidatedCertificateProps", jsii_struct_bases=[_DnsValidatedCertificateProps])
class DnsValidatedCertificateProps(_DnsValidatedCertificateProps):
    """
    Stability:
        experimental
    """
    hostedZone: aws_cdk.aws_route53.IHostedZone
    """Route 53 Hosted Zone used to perform DNS validation of the request.

    The zone
    must be authoritative for the domain name specified in the Certificate Request.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-certificatemanager.ICertificate")
class ICertificate(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ICertificateProxy

    @property
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> str:
        """The certificate's ARN.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _ICertificateProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-certificatemanager.ICertificate"
    @property
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> str:
        """The certificate's ARN.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "certificateArn")


@jsii.implements(ICertificate)
class Certificate(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-certificatemanager.Certificate"):
    """A certificate managed by AWS Certificate Manager.

    IMPORTANT: if you are creating a certificate as part of your stack, the stack
    will not complete creating until you read and follow the instructions in the
    email that you will receive.

    ACM will send validation emails to the following addresses:

    admin@domain.com
    administrator@domain.com
    hostmaster@domain.com
    postmaster@domain.com
    webmaster@domain.com

    For every domain that you register.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, domain_name: str, subject_alternative_names: typing.Optional[typing.List[str]]=None, validation_domains: typing.Optional[typing.Mapping[str,str]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            domainName: Fully-qualified domain name to request a certificate for. May contain wildcards, such as ``*.domain.com``.
            subjectAlternativeNames: Alternative domain names on your certificate. Use this to register alternative domain names that represent the same site. Default: - No additional FQDNs will be included as alternative domain names.
            validationDomains: What validation domain to use for every requested domain. Has to be a superdomain of the requested domain. Default: - Apex domain is used for every domain that's not overridden.

        Stability:
            experimental
        """
        props: CertificateProps = {"domainName": domain_name}

        if subject_alternative_names is not None:
            props["subjectAlternativeNames"] = subject_alternative_names

        if validation_domains is not None:
            props["validationDomains"] = validation_domains

        jsii.create(Certificate, self, [scope, id, props])

    @jsii.member(jsii_name="fromCertificateArn")
    @classmethod
    def from_certificate_arn(cls, scope: aws_cdk.cdk.Construct, id: str, certificate_arn: str) -> "ICertificate":
        """Import a certificate.

        Arguments:
            scope: -
            id: -
            certificateArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromCertificateArn", [scope, id, certificate_arn])

    @property
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> str:
        """The certificate's ARN.

        Stability:
            experimental
        """
        return jsii.get(self, "certificateArn")


@jsii.implements(ICertificate)
class DnsValidatedCertificate(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-certificatemanager.DnsValidatedCertificate"):
    """A certificate managed by AWS Certificate Manager.

    Will be automatically
    validated using DNS validation against the specified Route 53 hosted zone.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, hosted_zone: aws_cdk.aws_route53.IHostedZone, region: typing.Optional[str]=None, domain_name: str, subject_alternative_names: typing.Optional[typing.List[str]]=None, validation_domains: typing.Optional[typing.Mapping[str,str]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            hostedZone: Route 53 Hosted Zone used to perform DNS validation of the request. The zone must be authoritative for the domain name specified in the Certificate Request.
            region: AWS region that will host the certificate. This is needed especially for certificates used for CloudFront distributions, which require the region to be us-east-1. Default: the region the stack is deployed in.
            domainName: Fully-qualified domain name to request a certificate for. May contain wildcards, such as ``*.domain.com``.
            subjectAlternativeNames: Alternative domain names on your certificate. Use this to register alternative domain names that represent the same site. Default: - No additional FQDNs will be included as alternative domain names.
            validationDomains: What validation domain to use for every requested domain. Has to be a superdomain of the requested domain. Default: - Apex domain is used for every domain that's not overridden.

        Stability:
            experimental
        """
        props: DnsValidatedCertificateProps = {"hostedZone": hosted_zone, "domainName": domain_name}

        if region is not None:
            props["region"] = region

        if subject_alternative_names is not None:
            props["subjectAlternativeNames"] = subject_alternative_names

        if validation_domains is not None:
            props["validationDomains"] = validation_domains

        jsii.create(DnsValidatedCertificate, self, [scope, id, props])

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[str]:
        """Validate the current construct.

        This method can be implemented by derived constructs in order to perform
        validation logic. It is called on all constructs before synthesis.

        Stability:
            experimental
        """
        return jsii.invoke(self, "validate", [])

    @property
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> str:
        """The certificate's ARN.

        Stability:
            experimental
        """
        return jsii.get(self, "certificateArn")


__all__ = ["Certificate", "CertificateProps", "CfnCertificate", "CfnCertificateProps", "DnsValidatedCertificate", "DnsValidatedCertificateProps", "ICertificate", "__jsii_assembly__"]

publication.publish()
