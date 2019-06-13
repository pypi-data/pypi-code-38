from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='common-utilities',
    version='0.0.5',
    description="Common utilities",
    long_description=open('README.md', 'r').read(),
    long_description_content_type="text/markdown",
    url='',
    author='hacfox',
    author_email='zz.hacfox@gmail.com',
    packages=find_packages(exclude=[]),
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    install_requires=[],
    zip_safe=True
)
