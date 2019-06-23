from setuptools import setup

name = 'protex'

setup(
    name=name,
    version='0.1.0',
    description='Clean Latex sources without loosing track of positions',
    author='Théo (Lattay) Cavignac',
    author_email='theo.cavignac@gmail.com',
    packages=[name],
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    scripts=['bin/protex'],
    package_data={name: ['commands.json']},
    include_package_data=True,
    license='MIT',
)
