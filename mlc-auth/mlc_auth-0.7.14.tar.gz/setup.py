from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mlc_auth',
    packages=['mlc_auth'],
    description='Tools for a easy connection with the MLC authentication portal',
    version='0.7.14',
    url='https://gitlab.com/machine-learning-company/mlc-services/mlc-service-boilerplate',
    author='Niels Wijers',
    author_email='nielsjlwijers@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['pip','mlc-services','machine learning company', 'authentication', 'mlc-portal'],
    install_requires=[
        'flask',
        'flask_login',
        'argon2-cffi',
        'requests',
    ]
)

"""
To upload the package to pypi:
First you need to alter the version number in the setup properties.

Then execute the following command in you command line:
python setup.py sdist bdist_wheel

The above command will create a .tar.gz file in the dist directory.

To upload the the file to pypi:
python -m twine upload .\dist\mlc_auth-<!file version here!>.tar.gz

Upgrade your package in you project by executing the following command:
pip install mlc_auth --upgrade

"""
