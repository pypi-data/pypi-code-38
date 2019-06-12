import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='bulu-faq',
    version='0.2',
    packages=['faq', 'faq.migrations'],
    include_package_data=True,
    license='MIT License', 
    description='A simple Django app for FAQa',
    long_description=README,
    url='https://bulugroup.com',
    author='Tobin Brown',
    author_email='tobin@bulugroup.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)