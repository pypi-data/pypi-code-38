import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.cdk",
    "version": "0.34.0",
    "description": "AWS Cloud Development Kit Core Library",
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
        "aws_cdk.cdk",
        "aws_cdk.cdk._jsii"
    ],
    "package_data": {
        "aws_cdk.cdk._jsii": [
            "cdk@0.34.0.jsii.tgz"
        ],
        "aws_cdk.cdk": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.11.2",
        "publication>=0.0.3",
        "aws-cdk.cx-api~=0.34.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
