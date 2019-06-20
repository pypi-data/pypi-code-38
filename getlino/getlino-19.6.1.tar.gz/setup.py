from setuptools import setup

SETUP_INFO = dict(
    name='getlino',
    version='19.6.1',
    install_requires=['argh'],
    test_suite='tests',
    description="Get Lino application",
    long_description=u"""
    Get Lino application
    """,
    author='Luc Saffre',
    author_email='luc.saffre@gmail.com',
    url="http://lino-framework.org",
    license='BSD License',
    scripts=['getlino.py'],
    classifiers="""\
Programming Language :: Python
Programming Language :: Python :: 3
Development Status :: 1 - Planning
Environment :: Web Environment
Framework :: Django
Intended Audience :: Developers
Intended Audience :: System Administrators
License :: OSI Approved :: BSD License
Operating System :: OS Independent
Topic :: Office/Business :: Financial :: Accounting
""".splitlines())

SETUP_INFO.update(
    zip_safe=False,
    include_package_data=True)

if __name__ == '__main__':
    setup(**SETUP_INFO)
