import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = '0.19.0'

setup(
    name='dyools',
    version=version,
    description="dyools",
    long_description=README,
    classifiers=[],
    keywords='dyools',
    author='me',
    author_email='me@example.org',
    url='https://example.org',
    license='LGPL v3',
    zip_safe=True,
    py_modules=['dyools'],
    include_package_data=True,
    package_dir={},
    packages=['dyools'],
    install_requires=[
        'click',
        'future',
        'pyaml',
        'odoorpc',
        'python-dateutil',
        'flask',
        'prettytable',
        'click',
        'xlsxwriter',
        'xlrd',
        'requests',
        'psutil',
        'faker',
        'lxml',
        'polib',
        'terminaltables',
        'colorclass',
        'dateparser',
        'paramiko',
    ],
    setup_requires=['pytest-runner', ],
    tests_require=['pytest', ],
    entry_points='''
        [console_scripts]
        ws_agent=dyools:cli_ws_agent
        rpc=dyools:cli_rpc
        tool=dyools:cli_tool
        xml=dyools:cli_xml
        etl=dyools:cli_etl
        po=dyools:cli_po
        sign=dyools:cli_sign
        todo=dyools:cli_todo
        job=dyools:cli_job
        dhelp=dyools:cli_help
        deploy=dyools:cli_deploy
    ''',

)
