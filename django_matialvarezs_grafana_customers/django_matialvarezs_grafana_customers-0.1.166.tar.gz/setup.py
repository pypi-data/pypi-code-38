# from distutils.core import setup
# setup(
#   name = 'django-matialvarezs_grafana_customers',
#   packages = ['matialvarezs_grafana_customers'], # this must be the same as the name above
#   version = '0.1.1',
#   install_requires = [
#         'simplejson==3.13.2',
#   ],
#   include_package_data = True,
#   description = 'Easy handler',
#   author = 'Matias Alvarez Sabate',
#   author_email = 'matialvarezs@gmail.com',
#   classifiers = [
#     'Programming Language :: Python :: 3.5',
#   ],
# )


import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django_matialvarezs_grafana_customers',
    version='0.1.166',
    install_requires=[
        'matialvarezs-request-handler==0.1.6',
        'psycopg2==2.7.4',
        'django-ohm2-handlers-light==0.1.21'
    ],
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  # example license
    description='grafana apps handlers customers.',
    long_description=README,
    url='',
    author='Matias Alvarez Sabate',
    author_email='matialvarezs@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',  # replace "X.Y" as appropriate
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
