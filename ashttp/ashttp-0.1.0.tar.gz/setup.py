import ast
import re

from setuptools import find_packages, setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('ashttp.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='ashttp',
    version=version,
    description='Super fast asynchronous HTTP client.',
    author='Jiuli Gao',
    author_email='gaojiuli@gmail.com',
    url='https://github.com/gaojiuli/ashttp',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[
        'cchardet',
        'httptools',
    ],
    license='MIT',
    packages=find_packages(),
    py_modules=['ashttp'],
    include_package_data=True,
    zip_safe=False
)
