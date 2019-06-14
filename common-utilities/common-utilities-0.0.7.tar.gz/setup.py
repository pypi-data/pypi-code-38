from setuptools import find_packages, setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='common-utilities',
    version='0.0.7',
    description="Common utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='',
    author='hacfox',
    author_email='zz.hacfox@gmail.com',
    packages=find_packages(exclude=[]),
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[],
    zip_safe=False
)
