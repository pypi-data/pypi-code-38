import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='bee_django_course_simple',
    version='0.0.17',
    packages=['bee_django_course_simple'],
    include_package_data=True,
    description='A line of description',
    long_description=README,
    author='zhangyue',
    author_email='zhangyue@zhenpuedu.com',
    license='MIT',
    install_requires=[
        'Django>=1.11',
    ]
)
