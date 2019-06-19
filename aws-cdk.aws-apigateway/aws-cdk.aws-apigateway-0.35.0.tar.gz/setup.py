import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.aws-apigateway",
    "version": "0.35.0",
    "description": "The CDK Construct Library for AWS::ApiGateway",
    "url": "https://github.com/awslabs/aws-cdk",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "project_urls": {
        "Source": "https://github.com/awslabs/aws-cdk.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aws_cdk.aws_apigateway",
        "aws_cdk.aws_apigateway._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_apigateway._jsii": [
            "aws-apigateway@0.35.0.jsii.tgz"
        ],
        "aws_cdk.aws_apigateway": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.11.3",
        "publication>=0.0.3",
        "aws-cdk.aws-elasticloadbalancingv2~=0.35.0",
        "aws-cdk.aws-iam~=0.35.0",
        "aws-cdk.aws-lambda~=0.35.0",
        "aws-cdk.cdk~=0.35.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
