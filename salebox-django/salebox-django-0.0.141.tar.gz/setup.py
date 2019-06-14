# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='salebox-django',
    version='0.0.141',
    author=u'Jon Combe',
    author_email='jon@getsalebox.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django-mptt',
        'django-opposable-thumbs',
        'pyShipping-python3',
        'requests'
    ],
    url='https://getsalebox.com',
    license='BSD licence, see LICENCE file',
    description='Django ecommerce powered by Salebox',
    long_description='Connect a standalone Django ecommerce website to a GetSalebox.com backoffice',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe=False,
)
