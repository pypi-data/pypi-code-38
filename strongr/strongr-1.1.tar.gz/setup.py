from setuptools import setup, find_packages

setup(
    name='strongr',
    version='1.1',
    description='An elastic cloud command runner',
    author='Thomas Phil',
    author_email='thomas@tphil.nl',
    packages=find_packages(),  # auto detect packages
    install_requires=[
        'salt==2018.3.1'
        'jsonpickle==0.9.5',
        'cleo==0.6.1',
        'Flask==0.12.2',
        'dependency_injector==3.6.1',
        'filelock==2.0.12',
        'flask_restplus==0.10.1',
        'Flask_OAuthlib==0.9.4',
        'cmndr==1.0.5',
        'gunicorn==19.7.1',
        'SQLAlchemy==1.1.14',
        'PyYAML==3.12',
        'psutil==5.4.3',
        'celery==4.1.0',
        'redis==2.10.6',
        'statsd==3.2.2',
        'enum34==1.1.6',
        'schedule',
        'authlib==0.4.1',
        'mysqlclient',
        'tornado==4.5.2',
    ], #external packages as dependencies
    scripts=[
        'bin/strongr'
    ]
)
