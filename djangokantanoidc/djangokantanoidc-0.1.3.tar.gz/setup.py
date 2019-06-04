import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='djangokantanoidc',
    version='0.1.3',
    packages=['kantanoidc'],
    license='MIT',
    description='Helper app as oidc client',
    long_description=read('README.rst'),
    keywords='django oidc',
    url='https://github.com/mmiyajima2/django-kantanoidc',
    author='Masafumi Miyajima',
    author_email='mmiyajima2@gmail.com',
    install_requires=[
        'django',
        'requests',
        'urllib3>=1.24.2',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
