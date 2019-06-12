from setuptools import setup, find_packages

setup(
    name='celery_macrobase',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/mbcores/celery-macrobase',
    license='MIT',
    author='Alexey Shagaleev',
    author_email='alexey.shagaleev@yandex.ru',
    description='Celery driver for macrobase framework',
    install_requires=[
        'macrobase-driver>=0.0.14',
        'celery==4.3.0',
        'uvloop==0.12.1',
        'python-rapidjson==0.7.0',
        'structlog==19.1.0'
    ]
)
