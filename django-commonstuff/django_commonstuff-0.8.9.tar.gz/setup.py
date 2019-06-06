# -*- coding: utf-8 -*-
import os
import setuptools


README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setuptools.setup(
    name='django_commonstuff',
    version='0.8.9',
    packages=setuptools.find_packages(),  # packages=['commonstuff'],
    include_package_data=True,
    license='WTFPL License',
    description='Reusable app, what collects django-related code, used in most of my projects.',
    long_description=README,
    long_description_content_type="text/x-rst",
    author='Yuriy Zemskov',
    author_email='zemskyura@gmail.com',
    # url="",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django>=1.11,<2.3',
        'robot-detection>=0.3',
        'pytils',
        'csscompressor>=0.9.3',
        'jsmin>=2.1.6',
        'Pillow>=4.3.0',  # for ckeditoruploads
    ],
    extras_require={
        'mobilesupport': ['django-mobile >= 0.5.1',],
    }
)

