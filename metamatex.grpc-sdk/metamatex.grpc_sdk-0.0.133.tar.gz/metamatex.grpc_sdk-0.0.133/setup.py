import setuptools
from distutils.core import setup

setup(
    name='metamatex.grpc_sdk',
    packages=['metamatex.grpc_sdk'],
    version='0.0.133',
    description='',
    author='',
    author_email='',
    include_package_data=True,
    url='https://github.com/metamatex/grpc-sdk',
    download_url='',
    keywords=[],
    package_data={'metamatex.grpc_sdk':['*', '*/*', '*/*/*']},
    install_requires=[
        'googleapis-common-protos',
        'grpcio-tools'
    ],
)
