from setuptools import setup, find_packages


description = """\
A light weight framework for Object Detection."""

install_requires = [
    'nose2',
    'Pillow==5.2.0',
    'line-bot-sdk',
    'flask==1.0.2',
    'arrow==0.10.0',
    'six',
    'peewee==3.7.1',
    'wtf-peewee==3.0.0',
    'flask-admin==1.5.2',
    'lxml==4.2.4',
    'pathlib==1.0.1'
]


setup(
    name='eyewitness',
    version='1.0.10',
    description=description,
    author='Ching-Hua Yang',
    url='https://gitlab.com/penolove15/witness',
    install_requires=install_requires,
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    include_package_data=True
)
