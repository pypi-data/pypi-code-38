"""

Functions that will ensure that the ARN is returned if a string is passed.
If it is an object in troposphere, it will return GetAtt(obj, 'Arn') or Ref() depending on
what the object supports for return.
If it is a string, it must either comply to the last part of a ARN or be a full ARN
and match the ARN pattern

"""
import re
from troposphere import (
    AWS_REGION,
    AWS_ACCOUNT_ID
)
from troposphere import (
    ImportValue,
    Parameter,
    GetAtt,
    Sub,
    Ref
)
from troposphere.iam import (
    Role
)
from troposphere.s3 import Bucket
from troposphere.awslambda import Function
from troposphere.kms import (
    Key, Alias
)

from ozone.filters.regexes import (
    S3_ARN_PREFIX, S3_NAME, S3_ARN,
    IAM_ROLE_NAME, IAM_ROLE_ARN,
    LAMBDA_NAME, LAMBDA_ARN,
    LAMBDA_LAYER_VERSION, LAMBDA_LAYER_ARN,
    KMS_KEY_ARN, KMS_KEY_ID,
    KMS_ALIAS, KMS_ALIAS_ARN
)

def s3_bucket(bucket, any_object=False):
    """
    Args:
        bucket: represents the bucket object, or a function
    Returns:
        untouched if one of the functions supported
        string of the full ARN if the bucket name is given
        full ARN if full ARN is given and match S3 bucket ARN pattern
    """
    arn_pat = re.compile(S3_ARN)
    name_pat = re.compile(S3_NAME)
    if isinstance(bucket, (ImportValue, GetAtt, Sub, Ref)):
        return bucket
    elif isinstance(bucket, Parameter):
        if any_object:
            return Sub('arn:aws:s3:::{bucket}/*')
        else:
            return Sub('arn:aws:s3:::{bucket}')
    elif isinstance(bucket, Bucket):
        return GetAtt(bucket, 'Arn')
    elif isinstance(bucket, str):
        if arn_pat.match(bucket):
            return bucket
        elif name_pat.match(bucket):
            if any_object:
                return f'{S3_ARN_PREFIX}{bucket}/*'
            else:
                return f'{S3_ARN_PREFIX}{bucket}'
        else:
            raise ValueError('The S3 ARN must follow', S3_ARN)
    else:
        raise ValueError(
            'The S3 ARN must be computed with a function or follow the pattern',
            S3_ARN
        )

def iam_role(role):
    """
    Args:
        role: represents the role object, or a function
    Returns:
        untouched if one of the functions supported
        string of the full ARN if the role name is given
        full ARN if full ARN is given and match IAM role ARN pattern
    """
    arn_pattern = re.compile(IAM_ROLE_ARN)
    name_pattern = re.compile(IAM_ROLE_NAME)
    if isinstance(role, str):
        if name_pattern.match(role):
            role_arn = Sub(f'arn:aws:iam::${{AWS::AccountId}}:role/{role}')
        elif role.startswith('arn:aws:iam::') and arn_pattern.match(role):
            role_arn = role
        else:
            raise ValueError(
                'Role ARN must follow either the name or full arn patterns',
                IAM_ROLE_NAME,
                IAM_ROLE_ARN
            )
    elif isinstance(role, (Parameter, Role)):
        role_arn = GetAtt(role, 'Arn')
    elif isinstance(role, (GetAtt, Sub, Ref, ImportValue)):
        role_arn = role
    else:
        raise TypeError('role expected to be of type', str, ImportValue, Role, Sub, GetAtt, Ref)
    return role_arn


def lambda_function(function):
    """
    Args:
        function: represents the function object, or a function
    Returns:
        untouched if one of the functions supported
        string of the full ARN if the function name is given
        full ARN if full ARN is given and match function ARN pattern
    """
    arn_pattern = re.compile(LAMBDA_ARN)
    name_pattern = re.compile(LAMBDA_NAME)
    if isinstance(function, str):
        if name_pattern.match(function):
            function_arn = Sub(f'arn:aws:lambda:${{AWS::Region}}:${{AWS::AccountId}}:function:{function}')
        elif function.startswith('arn:aws:lambda:') and arn_pattern.match(function):
            function_arn = function
        else:
            raise ValueError(
                'Function ARN must follow either the name or full arn patterns',
                LAMBDA_NAME,
                LAMBDA_ARN
            )
    elif isinstance(function, (Parameter, Function)):
        function_arn = GetAtt(function, 'Arn')
    elif isinstance(function, (ImportValue, GetAtt, Sub, Ref)):
        function_arn = function
    else:
        raise TypeError('Function expected to be of type', str, Role, Sub, GetAtt, Ref, ImportValue)
    return function_arn


def lambda_layer(layer):
    """
    Args:
        layer: represents the layer object, or a function
    Returns:
        untouched if one of the functions supported
        string of the full ARN if the layer name is given
        full ARN if full ARN is given and match Lambda layer ARN pattern
    """
    arn_pattern = re.compile(LAMBDA_LAYER_ARN)
    version_pattern = re.compile(LAMBDA_LAYER_VERSION)
    if isinstance(layer, (GetAtt, Ref, Sub, ImportValue)):
        return layer
    elif isinstance(layer, str):
        if arn_pattern.match(layer):
            return layer
        elif version_pattern.match(layer):
            return Sub(f'arn:aws:lambda:${{AWS::Region}}:${{AWS::AccountId}}:layer:{layer}')
        else:
            raise ValueError(
                "Layer ARN expected of format"
                f"{LAMBDA_LAYER_ARN} or {LAMBDA_LAYER_VERSION}"
            )
    else:
        raise ValueError(
            'Layer does not comply to any required patterns of Functions'
        )


def kms_key(key):
    """
    Args:
        key: represents the key object, or a function
    Returns:
        untouched if one of the functions supported
        string of the full ARN if the key name is given
        full ARN if full ARN is given and match KMS key ARN pattern
    """
    arn_pattern = re.compile(KMS_KEY_ARN)
    id_pattern = re.compile(KMS_KEY_ID)
    if isinstance(key, (Ref, Sub, ImportValue, GetAtt)):
        return key
    if isinstance(key, (Parameter, Key)):
        return GetAtt(key, 'Arn')
    if isinstance(key, str):
        if arn_pattern.match(key):
            return key
        if id_pattern.match(key):
            return Sub(f'arn:aws:kms:${{AWS::Region}}:${{AWS::AccountId}}:key/{key}')
    else:
        raise ValueError('Key does not match pattern', KMS_KEY_ARN, KMS_KEY_ID)

def kms_alias(alias):
    """
    Args:
        alias: represents the alias object, or a function
    Returns:
        untouched if one of the functions supported
        string of the full ARN if the alias name is given
        full ARN if full ARN is given and match KMS Key alias ARN pattern
    """
    arn_pattern = re.compile(KMS_ALIAS_ARN)
    alias_pattern = re.compile(KMS_ALIAS)
    if isinstance(alias, (Ref, Sub, ImportValue, GetAtt)):
        return alias
    if isinstance(alias, (Parameter, Alias)):
        return GetAtt(alias, 'Arn')
    if isinstance(alias, str):
        if arn_pattern.match(alias):
            return alias
        if alias_pattern.match(alias):
            return Sub(f'arn:aws:kms:${{AWS::Region}}:${{AWS::AccountId}}:{alias}')
    else:
        raise ValueError('Alias  does not match pattern', alias, KMS_ALIAS, KMS_ALIAS_ARN)
