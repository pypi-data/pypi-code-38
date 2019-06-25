import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.core",
    "version": "0.36.0",
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
        "aws_cdk.core",
        "aws_cdk.core._jsii"
    ],
    "package_data": {
        "aws_cdk.core._jsii": [
            "core@0.36.0.jsii.tgz"
        ],
        "aws_cdk.core": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.12.1",
        "publication>=0.0.3",
        "aws-cdk.cx-api~=0.36.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
