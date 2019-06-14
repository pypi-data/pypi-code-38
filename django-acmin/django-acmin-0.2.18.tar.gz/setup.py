#!/usr/bin/env python


from setuptools import find_packages, setup

version = "0.2.18"

setup(
    name='django-acmin',
    version=version,
    author='Hike Li',
    author_email='hikelee@gmail.com',
    url='https://github.com/hikelee/django-acmin',
    description='Admin and API template for start a django web',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django :: 2.1',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
    license='BSD',
    packages=find_packages(),
    install_requires=[
        "Django>=2.2.2",
        "requests",
        "python_utils",
        "xlwt",
        "filelock",
        "djangorestframework"
    ],
    include_package_data=True,
    zip_safe=False,
)
