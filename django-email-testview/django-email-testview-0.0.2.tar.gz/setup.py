import os
import email_testview
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

install_requires = open('requirements.txt').read().splitlines()

# keep in sync with test_requirements.txt
dev_requires = [
    'pytest',
    'pytest-django',
    'pytest-cov',
    'fabric',
    'mixer',
]

setup(
    name='django-email-testview',
    version=email_testview.__version__,
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Strongly opinionated way to handle emails with Django',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/theartling/django-email-testview/',
    author='Martin Brochhaus',
    author_email='mbrochh@gmail.com',
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires,
    },
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
