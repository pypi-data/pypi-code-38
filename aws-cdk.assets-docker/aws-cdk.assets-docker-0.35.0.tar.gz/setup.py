import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.assets-docker",
    "version": "0.35.0",
    "description": "deprecated: moved to @aws-cdk/aws-ecr-assets",
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
        "aws_cdk.assets_docker._jsii"
    ],
    "package_data": {
        "aws_cdk.assets_docker._jsii": [
            "assets-docker@0.35.0.jsii.tgz"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.11.3",
        "publication>=0.0.3"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
