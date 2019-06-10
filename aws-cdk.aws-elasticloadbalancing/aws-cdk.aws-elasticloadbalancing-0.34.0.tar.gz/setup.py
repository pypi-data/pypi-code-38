import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.aws-elasticloadbalancing",
    "version": "0.34.0",
    "description": "CDK Constructs for AWS ElasticLoadBalancing",
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
        "aws_cdk.aws_elasticloadbalancing",
        "aws_cdk.aws_elasticloadbalancing._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_elasticloadbalancing._jsii": [
            "aws-elasticloadbalancing@0.34.0.jsii.tgz"
        ],
        "aws_cdk.aws_elasticloadbalancing": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.11.2",
        "publication>=0.0.3",
        "aws-cdk.aws-ec2~=0.34.0",
        "aws-cdk.cdk~=0.34.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
