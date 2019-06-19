from setuptools import setup


def parse_requirements(requirement_file):
    with open(requirement_file) as f:
        return f.readlines()


with open('./README.rst') as f:
    long_description = f.read()

setup(
    name='swimbundle_utils',
    packages=['swimbundle_utils'],
    version='1.1.6',
    description='Swimlane Bundle Utilities Package',
    author='Swimlane',
    author_email="info@swimlane.com",
    long_description=long_description,
    install_requires=parse_requirements('./requirements.txt'),
    keywords=['utilities', 'dictionary', 'flattening', 'rest'],
    classifiers=[],
)
