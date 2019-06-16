import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-apar',
    version='1.1.5.79',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  # example license
    description='Aparnik is a simple Django app to help about some common problems.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://www.aparnik.com/',
    author='Ali Zahedi Gol',
    author_email='zahedi@aparnik.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'boto3',
        'humanize',
        'django==2.2',
        'django-polymorphic',
        'django-rest-polymorphic',
        'pycryptodome',
        'django-s3direct',
        'djangorestframework',
        'python-dateutil',
        'kavenegar',
        'django-jalali-date',
        'Pillow',
        'fcm-django',
        'zeep',
        'django-dynamic-raw-id',
        'APScheduler',
        'django-filter==2.1.0',
        'django-ckeditor',
        'django-tagulous',
        'django-colorfield',
        'Faker',
        'python-magic',
        'pyPdf',
        'django-enumfield',
    ],
)
