import os
from setuptools import find_packages, setup


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
    #allod setup.py to be run from any path
    os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

    setup(
        name='MikhailP_django-blog',
        version='0.1',
        packages=find_packages(),
        include_package_date=True,
        license='MIT License',
        description='A simple Django app to conduct beauty blog.',
        long_description=README,
        url='http://wwww.hotmale.com/',
        author='Mikhail Panov',
        author_email='mihail52sh@mail.ru',
        classifiers=[
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    )