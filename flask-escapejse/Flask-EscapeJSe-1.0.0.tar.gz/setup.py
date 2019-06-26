"""
Flask-EscapeJSTV
-------------

Flask extension which registers a filter to escape curly braces for use in
javascript frameworks such as vue.js
"""

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Flask-EscapeJSe',
    version='1.0.0',
    url='https://github.com/akhilharihar/Flask-EscapeJSe',
    license='MIT',
    author='Akhil Harihar',
    author_email='hariharakhil@gmail.com',
    description='Escape curly braces in jinja template for use in JS \
        frameworks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=['flask_escapejse'],
    python_requires='>=3.0',
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'Jinja2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Development Status :: 5 - Production/Stable"
    ]
)
