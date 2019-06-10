import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.runtime-values",
    "version": "0.34.0",
    "description": "Runtime values support for the AWS CDK",
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
        "aws_cdk.runtime_values._jsii"
    ],
    "package_data": {
        "aws_cdk.runtime_values._jsii": [
            "runtime-values@0.34.0.jsii.tgz"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.11.2",
        "publication>=0.0.3"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
