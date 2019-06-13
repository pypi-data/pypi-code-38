from setuptools import setup, find_packages

setup(
    name='django_pmedien_all',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='All Pmedien Packages',
    long_description=open('README.md').read(),
    install_requires=[
        'django',
        'django-pmedien-default',
        'django-pmedien-export'
    ],
    url='http://www.pmedien.com',
    author='pmedien GmbH',
    author_email='nomail@pmedien.com'
)