import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.assets-docker",
    "version": "0.34.0",
    "description": "Docker image assets",
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
        "aws_cdk.assets_docker",
        "aws_cdk.assets_docker._jsii"
    ],
    "package_data": {
        "aws_cdk.assets_docker._jsii": [
            "assets-docker@0.34.0.jsii.tgz"
        ],
        "aws_cdk.assets_docker": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.11.2",
        "publication>=0.0.3",
        "aws-cdk.assets~=0.34.0",
        "aws-cdk.aws-cloudformation~=0.34.0",
        "aws-cdk.aws-ecr~=0.34.0",
        "aws-cdk.aws-iam~=0.34.0",
        "aws-cdk.aws-lambda~=0.34.0",
        "aws-cdk.aws-s3~=0.34.0",
        "aws-cdk.cdk~=0.34.0",
        "aws-cdk.cx-api~=0.34.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
