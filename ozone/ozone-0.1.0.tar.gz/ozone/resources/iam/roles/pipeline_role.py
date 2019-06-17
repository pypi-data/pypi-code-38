import sys
from troposphere import (
    GetAtt,
    Ref,
    Sub
)
from troposphere.iam import (
    Policy,
    Role
)
from ozone.resources.iam.roles import role_trust_policy
from ozone.filters.arns import (
    s3_bucket as filter_s3bucket
)


def _s3_access(**kwargs):
    s3_bucket = filter_s3bucket(kwargs['Bucket'], True)
    policy = Policy(
        PolicyName="LambdaLayers-S3Access",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    'Effect': 'Allow',
                    'Resource': [
                        s3_bucket
                ],
                    'Action': [
                        's3:PutObject',
                        's3:PutObjectVersion',
                        's3:GetObject',
                        's3:GetObjectVersion'
                    ]
                }
            ]
        }
    )
    return policy


def _invoke_lambda_access(**kwargs):
    policy = Policy(
        PolicyName="Pipeline-LambdaAccess",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    'Effect': 'Allow',
                    'Resource': [
                        '*'
                ],
                    'Action': [
                        'lambda:Invoke',
                        'lambda:InvokeFunction',
                        'lambda:List*',
                        'lambda:Get*'
                    ]
                }
            ]
        }
    )
    return policy


def _deploy_cloudformation_access(**kwargs):
    policy = Policy(
        PolicyName="LambdaLayers-PassRole",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": [
                        "iam:PassRole"
                    ],
                    "Resource": "*",
                    "Effect": "Allow",
                    "Condition": {
                        "StringEqualsIfExists": {
                            "iam:PassedToService": [
                                "cloudformation.amazonaws.com",
                            ]
                        }
                    }
                },
                {
                    "Effect": "Allow",
                    "Resource": "*",
                    "Action": [
                        "cloudformation:CreateStack",
                        "cloudformation:DeleteStack",
                        "cloudformation:DescribeStacks",
                        "cloudformation:UpdateStack",
                        "cloudformation:CreateChangeSet",
                        "cloudformation:DeleteChangeSet",
                        "cloudformation:DescribeChangeSet",
                        "cloudformation:ExecuteChangeSet",
                        "cloudformation:SetStackPolicy",
                        "cloudformation:ValidateTemplate"
                    ]
                }
            ]
        }
    )
    return policy


def _source_codecommit_access(**kwargs):
    policy = Policy(
        PolicyName="LambdaLayers-CodeCommitAccess",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement" : [
                {
                    "Resource": "*",
                    "Effect": "Allow",
                    "Action": [
                        "codecommit:CancelUploadArchive",
                        "codecommit:GetBranch",
                        "codecommit:GetCommit",
                        "codecommit:GetUploadArchiveStatus",
                        "codecommit:UploadArchive"
                    ]
                }
            ]
        }
    )
    return policy


def _build_codebuild_access(**kwargs):
    policy = Policy(
        PolicyName="LambdaLayers-CodeBuildAccess",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": [
                        "codebuild:BatchGetBuilds",
                        "codebuild:StartBuild"
                    ],
                    "Resource": "*",
                    "Effect": "Allow"
                }
            ]
        }
    )
    return policy



def pipelinerole_build(**kwargs):
    if not 'Bucket' in kwargs.keys():
        raise KeyError(f'Bucket is required to provide access to artifact store')
    policies = []
    policies.append(
        _s3_access(**kwargs)
    )
    stages = {
        'Source': ['AmazonS3', 'CodeCommit', 'AmazonEcr'],
        'Build': ['CodeBuild'],
        'Test': ['CodeBuild'],
        'Deploy': ['AmazonS3', 'Cloudformation', 'CodeDeploy', 'ServiceCatalog'],
        'Invoke': ['Lambda']
    }

    for stage in stages:
        for service in stages[stage]:
            key = f'Use{service}'
            func_name = f'_{stage.lower()}_{service.lower()}_access'
            if key in kwargs.keys() and kwargs[key]:
                try:
                    func = getattr(sys.modules[__name__], func_name)
                    policies.append(func(**kwargs))
                except KeyError as error:
                    raise KeyError(error)
                except AttributeError:
                    pass

    role = Role(
        "CodePipelineRole",
        AssumeRolePolicyDocument=role_trust_policy('codepipeline'),
        Policies=policies
    )
    return role
