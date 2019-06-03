# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import warnings
import pulumi
import pulumi.runtime
from .. import utilities, tables

class GetCertificateResult:
    """
    A collection of values returned by getCertificate.
    """
    def __init__(__self__, account_name=None, format=None, name=None, public_data=None, resource_group_name=None, thumbprint=None, thumbprint_algorithm=None, id=None):
        if account_name and not isinstance(account_name, str):
            raise TypeError("Expected argument 'account_name' to be a str")
        __self__.account_name = account_name
        if format and not isinstance(format, str):
            raise TypeError("Expected argument 'format' to be a str")
        __self__.format = format
        """
        The format of the certificate, such as `Cer` or `Pfx`.
        """
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        __self__.name = name
        if public_data and not isinstance(public_data, str):
            raise TypeError("Expected argument 'public_data' to be a str")
        __self__.public_data = public_data
        """
        The public key of the certificate.
        """
        if resource_group_name and not isinstance(resource_group_name, str):
            raise TypeError("Expected argument 'resource_group_name' to be a str")
        __self__.resource_group_name = resource_group_name
        if thumbprint and not isinstance(thumbprint, str):
            raise TypeError("Expected argument 'thumbprint' to be a str")
        __self__.thumbprint = thumbprint
        """
        The thumbprint of the certificate.
        """
        if thumbprint_algorithm and not isinstance(thumbprint_algorithm, str):
            raise TypeError("Expected argument 'thumbprint_algorithm' to be a str")
        __self__.thumbprint_algorithm = thumbprint_algorithm
        """
        The algorithm of the certificate thumbprint.
        """
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        __self__.id = id
        """
        id is the provider-assigned unique ID for this managed resource.
        """

async def get_certificate(account_name=None,name=None,resource_group_name=None,opts=None):
    """
    Use this data source to access information about an existing certificate in a Batch Account.
    """
    __args__ = dict()

    __args__['accountName'] = account_name
    __args__['name'] = name
    __args__['resourceGroupName'] = resource_group_name
    __ret__ = await pulumi.runtime.invoke('azure:batch/getCertificate:getCertificate', __args__, opts=opts)

    return GetCertificateResult(
        account_name=__ret__.get('accountName'),
        format=__ret__.get('format'),
        name=__ret__.get('name'),
        public_data=__ret__.get('publicData'),
        resource_group_name=__ret__.get('resourceGroupName'),
        thumbprint=__ret__.get('thumbprint'),
        thumbprint_algorithm=__ret__.get('thumbprintAlgorithm'),
        id=__ret__.get('id'))
