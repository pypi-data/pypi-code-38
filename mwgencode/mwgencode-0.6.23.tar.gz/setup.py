from setuptools import setup
from codecs import open
import os

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f),encoding='utf8').read()

setup(
    name='mwgencode',
    version='0.6.23',
    author='cxhjet',
    author_email='cxhjet@qq.com',
    description="根据starUML文档产生flask专案的代码",
    long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
    url='https://bitbucket.org/maxwin-inc/gencode/src/',  # Optional

    py_modules=['manage'],
    packages=['gencode',
              'gencode.gencode',
              'gencode.importxmi',
              'gencode.importmdj',
              'gencode.gencode.sample',
              'gencode.gencode.template',
              'gencode.gencode.template.tests',
              'gencode.gencode.sample.seeds'
           ],
    package_data={
        '': ['*.*']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
                      'mwutils>=0.1.29',
                      'mwauth>=0.4.26',
                      'mwsdk>=0.2.10',
                      'mwpermission>=0.1.21',
                      'mw-aiohttp-session>=0.1.4',
                      'mw-aiohttp-babel>=0.1.7',
                      'mw-aiohttp-security>=0.1.3',
                      'SQLAlchemy','pyJWT',
                      'python-consul',
                      'flask_migrate',
                      'flask-babel',
                      'Flask-Cors',
                      'Flask-Redis',
                      'geojson',
                      'redis==2.10.6',
                      'connexion==1.5.2',
                      # 'pymssql==2.1.3'
                      ],
    include_package_data=True,
    # 可以在cmd 执行产生代码
    entry_points={
        'console_scripts': ['gencode=manage:main']
    }
)
