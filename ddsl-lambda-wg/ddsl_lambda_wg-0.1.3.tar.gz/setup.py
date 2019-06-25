import setuptools
import re
import os
import ast

# parse version from locust/__init__.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')
_init_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "ddsl_lambda_wg", "__init__.py")
with open(_init_file, 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setuptools.setup(
    name="ddsl_lambda_wg",
    version=version,
    url="https://github.com/nimamahmoudi/ddsl_lambda_workload_generator",
    author="Nima Mahmoudi",
    author_email="nima_mahmoudi@live.com",
    description="This is a workload generator for aws lambda.",
    long_description=open('README.rst').read(),
    packages=setuptools.find_packages(),
    install_requires=['numpy'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={},

)

