from io import open

from setuptools import setup

# python setup.py sdist --formats=zip
# python setup.py sdist bdist_wheel
# twine upload dist/halo_flask-0.13.8.tar.gz -r pypitest

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='halo_flask',
    version='0.15.13',
    packages=['halo_flask', 'halo_flask.flask'],
    url='https://github.com/yoramk2/halo_flask',
    license='MIT License',
    author='yoramk2',
    author_email='yoramk2@yahoo.com',
    description='this is the Halo framework library for Flask',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Framework :: Flask',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
