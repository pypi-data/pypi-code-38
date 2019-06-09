from setuptools import setup, find_packages

setup(
    name='django-pgqueue',
    version='0.9.2',
    description='PostgreSQL-based task queue for Django',
    keywords='django postgres queue',
    packages=find_packages(),
    author='Max Poletaev',
    author_email='max.poletaev@gmail.com',
    url='https://github.com/zenwalker/django-pgqueue',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
    ],
)
