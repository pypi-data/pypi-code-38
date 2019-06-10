import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.aws-route53-targets",
    "version": "0.34.0",
    "description": "CDK Constructs for AWS Route53 Alias Targets",
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
        "aws_cdk.aws_route53_targets",
        "aws_cdk.aws_route53_targets._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_route53_targets._jsii": [
            "aws-route53-targets@0.34.0.jsii.tgz"
        ],
        "aws_cdk.aws_route53_targets": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.11.2",
        "publication>=0.0.3",
        "aws-cdk.aws-cloudfront~=0.34.0",
        "aws-cdk.aws-elasticloadbalancingv2~=0.34.0",
        "aws-cdk.aws-iam~=0.34.0",
        "aws-cdk.aws-route53~=0.34.0",
        "aws-cdk.cdk~=0.34.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
