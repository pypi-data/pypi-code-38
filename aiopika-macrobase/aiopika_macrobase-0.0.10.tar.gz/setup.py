from setuptools import setup, find_packages

setup(
    name='aiopika_macrobase',
    version='0.0.10',
    packages=find_packages(),
    url='https://github.com/mbcores/aiopika-macrobase',
    license='MIT',
    author='Alexey Shagaleev',
    author_email='alexey.shagaleev@yandex.ru',
    description='Aio-pika driver for macrobase framework',
    install_requires=[
        'macrobase-driver>=0.0.14',
        'aio-pika==5.5.3',
        'uvloop==0.12.1',
        'python-rapidjson==0.7.0',
        'structlog==19.1.0'
    ]
)
