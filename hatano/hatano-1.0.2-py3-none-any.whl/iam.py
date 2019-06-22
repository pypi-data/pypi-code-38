from hatano.util import Conf

import boto3
import json


trust = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": [
            "lambda.amazonaws.com",
            "apigateway.amazonaws.com",
            ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

example_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:*"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "xray:PutTraceSegments",
                "xray:PutTelemetryRecords"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:AttachNetworkInterface",
                "ec2:CreateNetworkInterface",
                "ec2:DeleteNetworkInterface",
                "ec2:DescribeInstances",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DetachNetworkInterface",
                "ec2:ModifyNetworkInterfaceAttribute",
                "ec2:ResetNetworkInterfaceAttribute"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": "arn:aws:s3:::*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "kinesis:*"
            ],
            "Resource": "arn:aws:kinesis:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sns:*"
            ],
            "Resource": "arn:aws:sns:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sqs:*"
            ],
            "Resource": "arn:aws:sqs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:*"
            ],
            "Resource": "arn:aws:dynamodb:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "route53:*"
            ],
            "Resource": "*"
        }
    ]
}

policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:*"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": "arn:aws:s3:::*"
        },
    ]
}


class IamRole:
    def __init__(self, stage, fnargs):
        self.stage = stage
        self.name = fnargs.get("name")
        c = Conf()
        self.project, stg_conf = c.get_stage(stage)
        self.iam = boto3.client('iam')
        self.fullname = f"{self.project}-{self.name}-{self.stage}"

    def lambda_role(self):
        role = self.iam.create_role(
                Path=f"/{self.project}/",
                RoleName=self.fullname,
                AssumeRolePolicyDocument=json.dumps(trust)
                )
        return role

    def delete_role(self):
        self.iam.delete_role(RoleName=self.fullname)

    def put_custom_policy(self):
        self.iam.put_role_policy(
                RoleName=self.fullname,
                PolicyName="hatano-permissions",
                PolicyDocument=json.dumps(policy))

    def delete_custom_policy(self):
        self.iam.delete_role_policy(
                RoleName=self.fullname,
                PolicyName="hatano-permissions")

