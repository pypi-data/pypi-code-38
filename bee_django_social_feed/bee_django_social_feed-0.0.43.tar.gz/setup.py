import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='bee_django_social_feed',
    version='0.0.43',
    packages=['bee_django_social_feed'],
    include_package_data=True,
    description='A line of description',
    long_description=README,
    author='huangwei',
    author_email='imonyse@gmail.com',
    license='MIT',
    install_requires=[
        'Django>=1.11',
    ]
)
