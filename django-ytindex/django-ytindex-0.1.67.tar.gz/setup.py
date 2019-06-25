import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-ytindex',
    version='0.1.67',
    packages=find_packages(),
    install_requires=['pytube','elasticsearch','google-api-python-client'],
    include_package_data=True,
    license='BSD License',
    description='Django app for managing a searchable index of Youtube videos',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://www.example.com/',
    author='ulfurk',
    author_email='ulfurk@ulfurk.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
