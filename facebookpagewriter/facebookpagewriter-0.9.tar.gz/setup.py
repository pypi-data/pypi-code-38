import uuid
from setuptools import setup, find_packages
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements


def get_requirements(source):
    try:
        install_reqs = parse_requirements(source, session=uuid.uuid1())
    except TypeError:
        # Older version of pip.
        install_reqs = parse_requirements(source)
    required = sorted(set([str(ir.req) for ir in install_reqs]))
    return list(required)

version = '0.9'

setup(
    name='facebookpagewriter',
    version=version,
    description='Automate Facebook page posting',
    long_description="",
    author='Aitzol Naberan',
    author_email='anaberan@codesyntax.com',
    url='http://github.com/codesyntax/facebookpagewriter',
    package_dir={'facebookpagewriter': 'facebookpagewriter'},
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    install_requires=get_requirements('requirements.txt'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
)
