from setuptools import find_packages, setup

NAME = 'flask-api-spec'
VERSION = '0.1.3'


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


setup(
    name=NAME,
    version=VERSION,
    packages=[t for t in find_packages() if t.startswith(
        NAME.replace('-', '_'))],
    include_package_data=True,
    install_requires=[str(ir) for ir in parse_requirements(
        './requirements.txt')],
    author='laberin',
    author_email='eseom@msn.com',
    url="http://github.com/laberin/flask-api-spec/",
    license="MIT",
    description="flask api toolset",
    platforms="any",
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)
