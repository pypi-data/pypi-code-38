import ast
import io
import re

from setuptools import setup, find_packages

with io.open('README.md', 'rt', encoding="utf8") as f:
    readme = f.read()

_description_re = re.compile(r'description\s+=\s+(?P<description>.*)')

with open('lektor_jsminify.py', 'rb') as f:
    description = str(ast.literal_eval(_description_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    author='maxbachmann',
    author_email='kontakt@maxbachmann.de',
    description=description,
    keywords='Lektor plugin',
    license='MIT',
    long_description=readme,
    long_description_content_type='text/markdown',
    name='lektor-jsminify',
    packages=find_packages(),
    py_modules=['lektor_jsminify'],
    url='https://github.com/maxbachmann/lektor-JSminify',
    version='0.2',
    install_requires  =  [
        "rjsmin",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Framework :: Lektor',
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        'lektor.plugins': [
            'jsminify = lektor_jsminify:JsminifyPlugin',
        ]
    }
)
