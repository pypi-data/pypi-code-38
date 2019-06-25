#!/usr/bin/env python

#
# Generated Mon Jun 10 11:49:52 2019 by generateDS.py version 2.32.0.
# Python 3.6.7 (default, Oct 22 2018, 11:32:17)  [GCC 8.2.0]
#
# Command line options:
#   ('-f', '')
#   ('-o', 's3_api.py')
#   ('-s', 's3_sub.py')
#   ('--super', 's3_api')
#
# Command line arguments:
#   schemas/AmazonS3.xsd
#
# Command line:
#   generateDS.py -f -o "s3_api.py" -s "s3_sub.py" --super="s3_api" schemas/AmazonS3.xsd
#
# Current working directory (os.getcwd()):
#   ks33requests
#

import os
import sys

from lxml import etree as etree_

from . import s3_api as supermod


def parsexml_(infile, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        parser = etree_.ETCompatXMLParser()
    try:
        if isinstance(infile, os.PathLike):
            infile = os.path.join(infile)
    except AttributeError:
        pass
    doc = etree_.parse(infile, parser=parser, **kwargs)
    return doc


#
# Globals
#

ExternalEncoding = ''


#
# Data representation classes
#


class CreateBucketSub(supermod.CreateBucket):
    def __init__(self, Bucket=None, AccessControlList=None, AWSAccessKeyId=None, Timestamp=None, Signature=None,
                 **kwargs_):
        super(CreateBucketSub, self).__init__(Bucket, AccessControlList, AWSAccessKeyId, Timestamp, Signature,
                                              **kwargs_)


supermod.CreateBucket.subclass = CreateBucketSub


# end class CreateBucketSub


class MetadataEntrySub(supermod.MetadataEntry):
    def __init__(self, Name=None, Value=None, **kwargs_):
        super(MetadataEntrySub, self).__init__(Name, Value, **kwargs_)


supermod.MetadataEntry.subclass = MetadataEntrySub


# end class MetadataEntrySub


class CreateBucketResponseSub(supermod.CreateBucketResponse):
    def __init__(self, CreateBucketReturn=None, **kwargs_):
        super(CreateBucketResponseSub, self).__init__(CreateBucketReturn, **kwargs_)


supermod.CreateBucketResponse.subclass = CreateBucketResponseSub


# end class CreateBucketResponseSub


class StatusSub(supermod.Status):
    def __init__(self, Code=None, Description=None, **kwargs_):
        super(StatusSub, self).__init__(Code, Description, **kwargs_)


supermod.Status.subclass = StatusSub


# end class StatusSub


class ResultSub(supermod.Result):
    def __init__(self, Status=None, extensiontype_=None, **kwargs_):
        super(ResultSub, self).__init__(Status, extensiontype_, **kwargs_)


supermod.Result.subclass = ResultSub


# end class ResultSub


class CreateBucketResultSub(supermod.CreateBucketResult):
    def __init__(self, BucketName=None, **kwargs_):
        super(CreateBucketResultSub, self).__init__(BucketName, **kwargs_)


supermod.CreateBucketResult.subclass = CreateBucketResultSub


# end class CreateBucketResultSub


class DeleteBucketSub(supermod.DeleteBucket):
    def __init__(self, Bucket=None, AWSAccessKeyId=None, Timestamp=None, Signature=None, Credential=None, **kwargs_):
        super(DeleteBucketSub, self).__init__(Bucket, AWSAccessKeyId, Timestamp, Signature, Credential, **kwargs_)


supermod.DeleteBucket.subclass = DeleteBucketSub


# end class DeleteBucketSub


class DeleteBucketResponseSub(supermod.DeleteBucketResponse):
    def __init__(self, DeleteBucketResponse_member=None, **kwargs_):
        super(DeleteBucketResponseSub, self).__init__(DeleteBucketResponse_member, **kwargs_)


supermod.DeleteBucketResponse.subclass = DeleteBucketResponseSub


# end class DeleteBucketResponseSub


class BucketLoggingStatusSub(supermod.BucketLoggingStatus):
    def __init__(self, LoggingEnabled=None, **kwargs_):
        super(BucketLoggingStatusSub, self).__init__(LoggingEnabled, **kwargs_)


supermod.BucketLoggingStatus.subclass = BucketLoggingStatusSub


# end class BucketLoggingStatusSub


class LoggingSettingsSub(supermod.LoggingSettings):
    def __init__(self, TargetBucket=None, TargetPrefix=None, TargetGrants=None, **kwargs_):
        super(LoggingSettingsSub, self).__init__(TargetBucket, TargetPrefix, TargetGrants, **kwargs_)


supermod.LoggingSettings.subclass = LoggingSettingsSub


# end class LoggingSettingsSub


class GetBucketLoggingStatusSub(supermod.GetBucketLoggingStatus):
    def __init__(self, Bucket=None, AWSAccessKeyId=None, Timestamp=None, Signature=None, Credential=None, **kwargs_):
        super(GetBucketLoggingStatusSub, self).__init__(Bucket, AWSAccessKeyId, Timestamp, Signature, Credential,
                                                        **kwargs_)


supermod.GetBucketLoggingStatus.subclass = GetBucketLoggingStatusSub


# end class GetBucketLoggingStatusSub


class GetBucketLoggingStatusResponseSub(supermod.GetBucketLoggingStatusResponse):
    def __init__(self, GetBucketLoggingStatusResponse_member=None, **kwargs_):
        super(GetBucketLoggingStatusResponseSub, self).__init__(GetBucketLoggingStatusResponse_member, **kwargs_)


supermod.GetBucketLoggingStatusResponse.subclass = GetBucketLoggingStatusResponseSub


# end class GetBucketLoggingStatusResponseSub


class SetBucketLoggingStatusSub(supermod.SetBucketLoggingStatus):
    def __init__(self, Bucket=None, AWSAccessKeyId=None, Timestamp=None, Signature=None, Credential=None,
                 BucketLoggingStatus=None, **kwargs_):
        super(SetBucketLoggingStatusSub, self).__init__(Bucket, AWSAccessKeyId, Timestamp, Signature, Credential,
                                                        BucketLoggingStatus, **kwargs_)


supermod.SetBucketLoggingStatus.subclass = SetBucketLoggingStatusSub


# end class SetBucketLoggingStatusSub


class SetBucketLoggingStatusResponseSub(supermod.SetBucketLoggingStatusResponse):
    def __init__(self, **kwargs_):
        super(SetBucketLoggingStatusResponseSub, self).__init__(**kwargs_)


supermod.SetBucketLoggingStatusResponse.subclass = SetBucketLoggingStatusResponseSub


# end class SetBucketLoggingStatusResponseSub


class GetObjectAccessControlPolicySub(supermod.GetObjectAccessControlPolicy):
    def __init__(self, Bucket=None, Key=None, AWSAccessKeyId=None, Timestamp=None, Signature=None, Credential=None,
                 **kwargs_):
        super(GetObjectAccessControlPolicySub, self).__init__(Bucket, Key, AWSAccessKeyId, Timestamp, Signature,
                                                              Credential, **kwargs_)


supermod.GetObjectAccessControlPolicy.subclass = GetObjectAccessControlPolicySub


# end class GetObjectAccessControlPolicySub


class GetObjectAccessControlPolicyResponseSub(supermod.GetObjectAccessControlPolicyResponse):
    def __init__(self, GetObjectAccessControlPolicyResponse_member=None, **kwargs_):
        super(GetObjectAccessControlPolicyResponseSub, self).__init__(GetObjectAccessControlPolicyResponse_member,
                                                                      **kwargs_)


supermod.GetObjectAccessControlPolicyResponse.subclass = GetObjectAccessControlPolicyResponseSub


# end class GetObjectAccessControlPolicyResponseSub


class GetBucketAccessControlPolicySub(supermod.GetBucketAccessControlPolicy):
    def __init__(self, Bucket=None, AWSAccessKeyId=None, Timestamp=None, Signature=None, Credential=None, **kwargs_):
        super(GetBucketAccessControlPolicySub, self).__init__(Bucket, AWSAccessKeyId, Timestamp, Signature, Credential,
                                                              **kwargs_)


supermod.GetBucketAccessControlPolicy.subclass = GetBucketAccessControlPolicySub


# end class GetBucketAccessControlPolicySub


class GetBucketAccessControlPolicyResponseSub(supermod.GetBucketAccessControlPolicyResponse):
    def __init__(self, GetBucketAccessControlPolicyResponse_member=None, **kwargs_):
        super(GetBucketAccessControlPolicyResponseSub, self).__init__(GetBucketAccessControlPolicyResponse_member,
                                                                      **kwargs_)


supermod.GetBucketAccessControlPolicyResponse.subclass = GetBucketAccessControlPolicyResponseSub


# end class GetBucketAccessControlPolicyResponseSub


class GranteeSub(supermod.Grantee):
    def __init__(self, extensiontype_=None, **kwargs_):
        super(GranteeSub, self).__init__(extensiontype_, **kwargs_)


supermod.Grantee.subclass = GranteeSub


# end class GranteeSub


class UserSub(supermod.User):
    def __init__(self, extensiontype_=None, **kwargs_):
        super(UserSub, self).__init__(extensiontype_, **kwargs_)


supermod.User.subclass = UserSub


# end class UserSub


class AmazonCustomerByEmailSub(supermod.AmazonCustomerByEmail):
    def __init__(self, EmailAddress=None, **kwargs_):
        super(AmazonCustomerByEmailSub, self).__init__(EmailAddress, **kwargs_)


supermod.AmazonCustomerByEmail.subclass = AmazonCustomerByEmailSub


# end class AmazonCustomerByEmailSub


class CanonicalUserSub(supermod.CanonicalUser):
    def __init__(self, ID=None, DisplayName=None, **kwargs_):
        super(CanonicalUserSub, self).__init__(ID, DisplayName, **kwargs_)


supermod.CanonicalUser.subclass = CanonicalUserSub


# end class CanonicalUserSub


class GroupSub(supermod.Group):
    def __init__(self, URI=None, **kwargs_):
        super(GroupSub, self).__init__(URI, **kwargs_)


supermod.Group.subclass = GroupSub


# end class GroupSub


class GrantSub(supermod.Grant):
    def __init__(self, Grantee=None, Permission=None, **kwargs_):
        super(GrantSub, self).__init__(Grantee, Permission, **kwargs_)


supermod.Grant.subclass = GrantSub


# end class GrantSub


class AccessControlListSub(supermod.AccessControlList):
    def __init__(self, Grant=None, **kwargs_):
        super(AccessControlListSub, self).__init__(Grant, **kwargs_)


supermod.AccessControlList.subclass = AccessControlListSub


# end class AccessControlListSub


class CreateBucketConfigurationSub(supermod.CreateBucketConfiguration):
    def __init__(self, LocationConstraint=None, **kwargs_):
        super(CreateBucketConfigurationSub, self).__init__(LocationConstraint, **kwargs_)


supermod.CreateBucketConfiguration.subclass = CreateBucketConfigurationSub


# end class CreateBucketConfigurationSub


class LocationConstraintSub(supermod.LocationConstraint):
    def __init__(self, valueOf_=None, **kwargs_):
        super(LocationConstraintSub, self).__init__(valueOf_, **kwargs_)


supermod.LocationConstraint.subclass = LocationConstraintSub


# end class LocationConstraintSub


class AccessControlPolicySub(supermod.AccessControlPolicy):
    def __init__(self, Owner=None, AccessControlList=None, **kwargs_):
        super(AccessControlPolicySub, self).__init__(Owner, AccessControlList, **kwargs_)


supermod.AccessControlPolicy.subclass = AccessControlPolicySub


# end class AccessControlPolicySub


class SetObjectAccessControlPolicySub(supermod.SetObjectAccessControlPolicy):
    def __init__(self, Bucket=None, Key=None, AccessControlList=None, AWSAccessKeyId=None, Timestamp=None,
                 Signature=None, Credential=None, **kwargs_):
        super(SetObjectAccessControlPolicySub, self).__init__(Bucket, Key, AccessControlList, AWSAccessKeyId, Timestamp,
                                                              Signature, Credential, **kwargs_)


supermod.SetObjectAccessControlPolicy.subclass = SetObjectAccessControlPolicySub


# end class SetObjectAccessControlPolicySub


class SetObjectAccessControlPolicyResponseSub(supermod.SetObjectAccessControlPolicyResponse):
    def __init__(self, **kwargs_):
        super(SetObjectAccessControlPolicyResponseSub, self).__init__(**kwargs_)


supermod.SetObjectAccessControlPolicyResponse.subclass = SetObjectAccessControlPolicyResponseSub


# end class SetObjectAccessControlPolicyResponseSub


class SetBucketAccessControlPolicySub(supermod.SetBucketAccessControlPolicy):
    def __init__(self, Bucket=None, AccessControlList=None, AWSAccessKeyId=None, Timestamp=None, Signature=None,
                 Credential=None, **kwargs_):
        super(SetBucketAccessControlPolicySub, self).__init__(Bucket, AccessControlList, AWSAccessKeyId, Timestamp,
                                                              Signature, Credential, **kwargs_)


supermod.SetBucketAccessControlPolicy.subclass = SetBucketAccessControlPolicySub


# end class SetBucketAccessControlPolicySub


class SetBucketAccessControlPolicyResponseSub(supermod.SetBucketAccessControlPolicyResponse):
    def __init__(self, **kwargs_):
        super(SetBucketAccessControlPolicyResponseSub, self).__init__(**kwargs_)


supermod.SetBucketAccessControlPolicyResponse.subclass = SetBucketAccessControlPolicyResponseSub


# end class SetBucketAccessControlPolicyResponseSub


class GetObjectSub(supermod.GetObject):
    def __init__(self, Bucket=None, Key=None, GetMetadata=None, GetData=None, InlineData=None, AWSAccessKeyId=None,
                 Timestamp=None, Signature=None, Credential=None, **kwargs_):
        super(GetObjectSub, self).__init__(Bucket, Key, GetMetadata, GetData, InlineData, AWSAccessKeyId, Timestamp,
                                           Signature, Credential, **kwargs_)


supermod.GetObject.subclass = GetObjectSub


# end class GetObjectSub


class GetObjectResponseSub(supermod.GetObjectResponse):
    def __init__(self, GetObjectResponse_member=None, **kwargs_):
        super(GetObjectResponseSub, self).__init__(GetObjectResponse_member, **kwargs_)


supermod.GetObjectResponse.subclass = GetObjectResponseSub


# end class GetObjectResponseSub


class GetObjectResultSub(supermod.GetObjectResult):
    def __init__(self, Status=None, Metadata=None, Data=None, LastModified=None, ETag=None, **kwargs_):
        super(GetObjectResultSub, self).__init__(Status, Metadata, Data, LastModified, ETag, **kwargs_)


supermod.GetObjectResult.subclass = GetObjectResultSub


# end class GetObjectResultSub


class GetObjectExtendedSub(supermod.GetObjectExtended):
    def __init__(self, Bucket=None, Key=None, GetMetadata=None, GetData=None, InlineData=None, ByteRangeStart=None,
                 ByteRangeEnd=None, IfModifiedSince=None, IfUnmodifiedSince=None, IfMatch=None, IfNoneMatch=None,
                 ReturnCompleteObjectOnConditionFailure=None, AWSAccessKeyId=None, Timestamp=None, Signature=None,
                 Credential=None, **kwargs_):
        super(GetObjectExtendedSub, self).__init__(Bucket, Key, GetMetadata, GetData, InlineData, ByteRangeStart,
                                                   ByteRangeEnd, IfModifiedSince, IfUnmodifiedSince, IfMatch,
                                                   IfNoneMatch, ReturnCompleteObjectOnConditionFailure, AWSAccessKeyId,
                                                   Timestamp, Signature, Credential, **kwargs_)


supermod.GetObjectExtended.subclass = GetObjectExtendedSub


# end class GetObjectExtendedSub


class GetObjectExtendedResponseSub(supermod.GetObjectExtendedResponse):
    def __init__(self, GetObjectResponse=None, **kwargs_):
        super(GetObjectExtendedResponseSub, self).__init__(GetObjectResponse, **kwargs_)


supermod.GetObjectExtendedResponse.subclass = GetObjectExtendedResponseSub


# end class GetObjectExtendedResponseSub


class PutObjectSub(supermod.PutObject):
    def __init__(self, Bucket=None, Key=None, Metadata=None, ContentLength=None, AccessControlList=None,
                 StorageClass=None, AWSAccessKeyId=None, Timestamp=None, Signature=None, Credential=None, **kwargs_):
        super(PutObjectSub, self).__init__(Bucket, Key, Metadata, ContentLength, AccessControlList, StorageClass,
                                           AWSAccessKeyId, Timestamp, Signature, Credential, **kwargs_)


supermod.PutObject.subclass = PutObjectSub


# end class PutObjectSub


class PutObjectResponseSub(supermod.PutObjectResponse):
    def __init__(self, PutObjectResponse_member=None, **kwargs_):
        super(PutObjectResponseSub, self).__init__(PutObjectResponse_member, **kwargs_)


supermod.PutObjectResponse.subclass = PutObjectResponseSub


# end class PutObjectResponseSub


class PutObjectResultSub(supermod.PutObjectResult):
    def __init__(self, ETag=None, LastModified=None, **kwargs_):
        super(PutObjectResultSub, self).__init__(ETag, LastModified, **kwargs_)


supermod.PutObjectResult.subclass = PutObjectResultSub


# end class PutObjectResultSub


class PutObjectInlineSub(supermod.PutObjectInline):
    def __init__(self, Bucket=None, Key=None, Metadata=None, Data=None, ContentLength=None, AccessControlList=None,
                 StorageClass=None, AWSAccessKeyId=None, Timestamp=None, Signature=None, Credential=None, **kwargs_):
        super(PutObjectInlineSub, self).__init__(Bucket, Key, Metadata, Data, ContentLength, AccessControlList,
                                                 StorageClass, AWSAccessKeyId, Timestamp, Signature, Credential,
                                                 **kwargs_)


supermod.PutObjectInline.subclass = PutObjectInlineSub


# end class PutObjectInlineSub


class PutObjectInlineResponseSub(supermod.PutObjectInlineResponse):
    def __init__(self, PutObjectInlineResponse_member=None, **kwargs_):
        super(PutObjectInlineResponseSub, self).__init__(PutObjectInlineResponse_member, **kwargs_)


supermod.PutObjectInlineResponse.subclass = PutObjectInlineResponseSub


# end class PutObjectInlineResponseSub


class DeleteObjectSub(supermod.DeleteObject):
    def __init__(self, Bucket=None, Key=None, AWSAccessKeyId=None, Timestamp=None, Signature=None, Credential=None,
                 **kwargs_):
        super(DeleteObjectSub, self).__init__(Bucket, Key, AWSAccessKeyId, Timestamp, Signature, Credential, **kwargs_)


supermod.DeleteObject.subclass = DeleteObjectSub


# end class DeleteObjectSub


class DeleteObjectResponseSub(supermod.DeleteObjectResponse):
    def __init__(self, DeleteObjectResponse_member=None, **kwargs_):
        super(DeleteObjectResponseSub, self).__init__(DeleteObjectResponse_member, **kwargs_)


supermod.DeleteObjectResponse.subclass = DeleteObjectResponseSub


# end class DeleteObjectResponseSub


class ListBucketSub(supermod.ListBucket):
    def __init__(self, Bucket=None, Prefix=None, Marker=None, MaxKeys=None, Delimiter=None, AWSAccessKeyId=None,
                 Timestamp=None, Signature=None, Credential=None, **kwargs_):
        super(ListBucketSub, self).__init__(Bucket, Prefix, Marker, MaxKeys, Delimiter, AWSAccessKeyId, Timestamp,
                                            Signature, Credential, **kwargs_)


supermod.ListBucket.subclass = ListBucketSub


# end class ListBucketSub


class ListBucketResponseSub(supermod.ListBucketResponse):
    def __init__(self, ListBucketResponse_member=None, **kwargs_):
        super(ListBucketResponseSub, self).__init__(ListBucketResponse_member, **kwargs_)


supermod.ListBucketResponse.subclass = ListBucketResponseSub


# end class ListBucketResponseSub


class ListVersionsResponseSub(supermod.ListVersionsResponse):
    def __init__(self, ListVersionsResponse_member=None, **kwargs_):
        super(ListVersionsResponseSub, self).__init__(ListVersionsResponse_member, **kwargs_)


supermod.ListVersionsResponse.subclass = ListVersionsResponseSub


# end class ListVersionsResponseSub


class ListEntrySub(supermod.ListEntry):
    def __init__(self, Key=None, LastModified=None, ETag=None, Size=None, Owner=None, StorageClass=None, **kwargs_):
        super(ListEntrySub, self).__init__(Key, LastModified, ETag, Size, Owner, StorageClass, **kwargs_)


supermod.ListEntry.subclass = ListEntrySub


# end class ListEntrySub


class VersionEntrySub(supermod.VersionEntry):
    def __init__(self, Key=None, VersionId=None, IsLatest=None, LastModified=None, ETag=None, Size=None, Owner=None,
                 StorageClass=None, **kwargs_):
        super(VersionEntrySub, self).__init__(Key, VersionId, IsLatest, LastModified, ETag, Size, Owner, StorageClass,
                                              **kwargs_)


supermod.VersionEntry.subclass = VersionEntrySub


# end class VersionEntrySub


class DeleteMarkerEntrySub(supermod.DeleteMarkerEntry):
    def __init__(self, Key=None, VersionId=None, IsLatest=None, LastModified=None, Owner=None, **kwargs_):
        super(DeleteMarkerEntrySub, self).__init__(Key, VersionId, IsLatest, LastModified, Owner, **kwargs_)


supermod.DeleteMarkerEntry.subclass = DeleteMarkerEntrySub


# end class DeleteMarkerEntrySub


class PrefixEntrySub(supermod.PrefixEntry):
    def __init__(self, Prefix=None, **kwargs_):
        super(PrefixEntrySub, self).__init__(Prefix, **kwargs_)


supermod.PrefixEntry.subclass = PrefixEntrySub


# end class PrefixEntrySub


class ListBucketResultSub(supermod.ListBucketResult):
    def __init__(self, Metadata=None, Name=None, Prefix=None, Marker=None, NextMarker=None, MaxKeys=None,
                 Delimiter=None, IsTruncated=None, Contents=None, CommonPrefixes=None, **kwargs_):
        super(ListBucketResultSub, self).__init__(Metadata, Name, Prefix, Marker, NextMarker, MaxKeys, Delimiter,
                                                  IsTruncated, Contents, CommonPrefixes, **kwargs_)


supermod.ListBucketResult.subclass = ListBucketResultSub


# end class ListBucketResultSub


class ListVersionsResultSub(supermod.ListVersionsResult):
    def __init__(self, Metadata=None, Name=None, Prefix=None, KeyMarker=None, VersionIdMarker=None, NextKeyMarker=None,
                 NextVersionIdMarker=None, MaxKeys=None, Delimiter=None, IsTruncated=None, Version=None,
                 DeleteMarker=None, CommonPrefixes=None, **kwargs_):
        super(ListVersionsResultSub, self).__init__(Metadata, Name, Prefix, KeyMarker, VersionIdMarker, NextKeyMarker,
                                                    NextVersionIdMarker, MaxKeys, Delimiter, IsTruncated, Version,
                                                    DeleteMarker, CommonPrefixes, **kwargs_)


supermod.ListVersionsResult.subclass = ListVersionsResultSub


# end class ListVersionsResultSub


class ListAllMyBucketsSub(supermod.ListAllMyBuckets):
    def __init__(self, AWSAccessKeyId=None, Timestamp=None, Signature=None, **kwargs_):
        super(ListAllMyBucketsSub, self).__init__(AWSAccessKeyId, Timestamp, Signature, **kwargs_)


supermod.ListAllMyBuckets.subclass = ListAllMyBucketsSub


# end class ListAllMyBucketsSub


class ListAllMyBucketsResponseSub(supermod.ListAllMyBucketsResponse):
    def __init__(self, ListAllMyBucketsResponse_member=None, **kwargs_):
        super(ListAllMyBucketsResponseSub, self).__init__(ListAllMyBucketsResponse_member, **kwargs_)


supermod.ListAllMyBucketsResponse.subclass = ListAllMyBucketsResponseSub


# end class ListAllMyBucketsResponseSub


class ListAllMyBucketsEntrySub(supermod.ListAllMyBucketsEntry):
    def __init__(self, Name=None, CreationDate=None, **kwargs_):
        super(ListAllMyBucketsEntrySub, self).__init__(Name, CreationDate, **kwargs_)


supermod.ListAllMyBucketsEntry.subclass = ListAllMyBucketsEntrySub


# end class ListAllMyBucketsEntrySub


class ListAllMyBucketsResultSub(supermod.ListAllMyBucketsResult):
    def __init__(self, Owner=None, Buckets=None, **kwargs_):
        super(ListAllMyBucketsResultSub, self).__init__(Owner, Buckets, **kwargs_)


supermod.ListAllMyBucketsResult.subclass = ListAllMyBucketsResultSub


# end class ListAllMyBucketsResultSub


class ListAllMyBucketsListSub(supermod.ListAllMyBucketsList):
    def __init__(self, Bucket=None, **kwargs_):
        super(ListAllMyBucketsListSub, self).__init__(Bucket, **kwargs_)


supermod.ListAllMyBucketsList.subclass = ListAllMyBucketsListSub


# end class ListAllMyBucketsListSub


class PostResponseSub(supermod.PostResponse):
    def __init__(self, Location=None, Bucket=None, Key=None, ETag=None, **kwargs_):
        super(PostResponseSub, self).__init__(Location, Bucket, Key, ETag, **kwargs_)


supermod.PostResponse.subclass = PostResponseSub


# end class PostResponseSub


class CopyObjectSub(supermod.CopyObject):
    def __init__(self, SourceBucket=None, SourceKey=None, DestinationBucket=None, DestinationKey=None,
                 MetadataDirective=None, Metadata=None, AccessControlList=None, CopySourceIfModifiedSince=None,
                 CopySourceIfUnmodifiedSince=None, CopySourceIfMatch=None, CopySourceIfNoneMatch=None,
                 StorageClass=None, AWSAccessKeyId=None, Timestamp=None, Signature=None, Credential=None, **kwargs_):
        super(CopyObjectSub, self).__init__(SourceBucket, SourceKey, DestinationBucket, DestinationKey,
                                            MetadataDirective, Metadata, AccessControlList, CopySourceIfModifiedSince,
                                            CopySourceIfUnmodifiedSince, CopySourceIfMatch, CopySourceIfNoneMatch,
                                            StorageClass, AWSAccessKeyId, Timestamp, Signature, Credential, **kwargs_)


supermod.CopyObject.subclass = CopyObjectSub


# end class CopyObjectSub


class CopyObjectResponseSub(supermod.CopyObjectResponse):
    def __init__(self, CopyObjectResult=None, **kwargs_):
        super(CopyObjectResponseSub, self).__init__(CopyObjectResult, **kwargs_)


supermod.CopyObjectResponse.subclass = CopyObjectResponseSub


# end class CopyObjectResponseSub


class CopyObjectResultSub(supermod.CopyObjectResult):
    def __init__(self, LastModified=None, ETag=None, **kwargs_):
        super(CopyObjectResultSub, self).__init__(LastModified, ETag, **kwargs_)


supermod.CopyObjectResult.subclass = CopyObjectResultSub


# end class CopyObjectResultSub


class RequestPaymentConfigurationSub(supermod.RequestPaymentConfiguration):
    def __init__(self, Payer=None, **kwargs_):
        super(RequestPaymentConfigurationSub, self).__init__(Payer, **kwargs_)


supermod.RequestPaymentConfiguration.subclass = RequestPaymentConfigurationSub


# end class RequestPaymentConfigurationSub


class VersioningConfigurationSub(supermod.VersioningConfiguration):
    def __init__(self, Status=None, MfaDelete=None, **kwargs_):
        super(VersioningConfigurationSub, self).__init__(Status, MfaDelete, **kwargs_)


supermod.VersioningConfiguration.subclass = VersioningConfigurationSub


# end class VersioningConfigurationSub


class NotificationConfigurationSub(supermod.NotificationConfiguration):
    def __init__(self, TopicConfiguration=None, **kwargs_):
        super(NotificationConfigurationSub, self).__init__(TopicConfiguration, **kwargs_)


supermod.NotificationConfiguration.subclass = NotificationConfigurationSub


# end class NotificationConfigurationSub


class TopicConfigurationSub(supermod.TopicConfiguration):
    def __init__(self, Topic=None, Event=None, **kwargs_):
        super(TopicConfigurationSub, self).__init__(Topic, Event, **kwargs_)


supermod.TopicConfiguration.subclass = TopicConfigurationSub


# end class TopicConfigurationSub


def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    rootClass = supermod.GDSClassesMapping.get(tag)
    if rootClass is None and hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'CreateBucket'
        rootClass = supermod.CreateBucket
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='xmlns:tns="http://s3.amazonaws.com/doc/2006-03-01/"',
            pretty_print=True)
    return rootObj


def parseEtree(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'CreateBucket'
        rootClass = supermod.CreateBucket
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    mapping = {}
    rootElement = rootObj.to_etree(None, name_=rootTag, mapping_=mapping)
    reverse_mapping = rootObj.gds_reverse_node_mapping(mapping)
    if not silence:
        content = etree_.tostring(
            rootElement, pretty_print=True,
            xml_declaration=True, encoding="utf-8")
        sys.stdout.write(content)
        sys.stdout.write('\n')
    return rootObj, rootElement, mapping, reverse_mapping


def parseString(inString, silence=False):
    if sys.version_info.major == 2:
        from StringIO import StringIO
    else:
        from io import BytesIO as StringIO
    parser = None
    doc = parsexml_(StringIO(inString), parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'CreateBucket'
        rootClass = supermod.CreateBucket
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='xmlns:tns="http://s3.amazonaws.com/doc/2006-03-01/"')
    return rootObj


def parseLiteral(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'CreateBucket'
        rootClass = supermod.CreateBucket
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    if not silence:
        sys.stdout.write('#from s3_api import *\n\n')
        sys.stdout.write('import s3_api as model_\n\n')
        sys.stdout.write('rootObj = model_.rootClass(\n')
        rootObj.exportLiteral(sys.stdout, 0, name_=rootTag)
        sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""


def usage():
    print(USAGE_TEXT)
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    parse(infilename)


if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    main()
