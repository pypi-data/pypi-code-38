import boto3
import time


def make_config(origin_domain, origin_id, access_id, path='/'):
    return {'Aliases': {'Quantity': 0},
     'CacheBehaviors': {'Quantity': 0},
     'CallerReference': str(time.time()),
     'Comment': '',
     'CustomErrorResponses': {'Quantity': 0},
     'DefaultCacheBehavior': {'AllowedMethods': {'CachedMethods': {'Items': ['HEAD',
                                                                             'GET'],
                                                                   'Quantity': 2},
                                                 'Items': ['HEAD', 'GET'],
                                                 'Quantity': 2},
                              'Compress': False,
                              'DefaultTTL': 86400,
                              'FieldLevelEncryptionId': '',
                              'ForwardedValues': {'Cookies': {'Forward': 'none'},
                                                  'Headers': {'Items': ['Access-Control-Request-Headers',
                                                                        'Access-Control-Request-Method',
                                                                        'Origin'],
                                                              'Quantity': 3},
                                                  'QueryString': False,
                                                  'QueryStringCacheKeys': {'Quantity': 0}},
                              'LambdaFunctionAssociations': {'Quantity': 0},
                              'MaxTTL': 31536000,
                              'MinTTL': 0,
                              'SmoothStreaming': False,
                              'TargetOriginId': origin_id,
                              'TrustedSigners': {'Enabled': False, 'Quantity': 0},
                              'ViewerProtocolPolicy': 'redirect-to-https'},
     'DefaultRootObject': '',
     'Enabled': True,
     'HttpVersion': 'http2',
     'IsIPV6Enabled': True,
     'Logging': {'Bucket': '',
                 'Enabled': False,
                 'IncludeCookies': False,
                 'Prefix': ''},
     'OriginGroups': {'Quantity': 0},
     'Origins': {'Items': [{'CustomHeaders': {'Quantity': 0},
                            'DomainName': origin_domain,
                            'Id': origin_id,
                            'OriginPath': path,
                            'S3OriginConfig': {'OriginAccessIdentity': f'origin-access-identity/cloudfront/{access_id}'}}],
                 'Quantity': 1},
     'PriceClass': 'PriceClass_All',
     'Restrictions': {'GeoRestriction': {'Quantity': 0, 'RestrictionType': 'none'}},
     'ViewerCertificate': {'CertificateSource': 'cloudfront',
                           'CloudFrontDefaultCertificate': True,
                           'MinimumProtocolVersion': 'TLSv1'},
     'WebACLId': ''}



class CloudFront:
    def __init__(self, proj, stage, path='/'):
        self.cf = boto3.client('cloudfront')
        self.proj = proj
        self.stage = stage
        self.path = path

    def _create_access_identity(self):
        name = f"access-identity-{self.proj}-{self.stage}"
        resp = self.cf.create_cloud_front_origin_access_identity(
                CloudFrontOriginAccessIdentityConfig={
                    "CallerReference": str(time.time()),
                    "Comment": name}
                )
        access_id = resp['CloudFrontOriginAccessIdentity']['Id']
        return access_id

    def _create_distribution(self, origin_domain, origin_id, access_id):
        cfg = make_config(origin_domain, origin_id, access_id, path=self.path)
        resp = self.cf.create_distribution(DistributionConfig=cfg)
        return resp['Distribution']

    def create_distribution_s3(self, bucket_name):
        o_domain = f"{bucket_name}.s3.amazonaws.com"
        o_id = f"S3-{bucket_name}"
        access_id = self._create_access_identity()
        return self._create_distribution(o_domain, o_id, access_id)
