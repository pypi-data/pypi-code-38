import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='dashboards-app-blero',
    version='1.1',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    license='MIT License',  # example license
    description='Blero Dashboards',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://www.blero.dev/',
    author='Blero',
    author_email='info@blero.dev',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
