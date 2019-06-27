from setuptools import setup, find_packages
import os

version = '1.6.2'
maintainer = 'Mathias Leimgruber'

tests_require = [
    'ftw.builder',
    'ftw.testing',
    'ftw.slider [tests]',
    'ftw.testbrowser',
    'plone.app.testing',
    'plone.testing',
]

extras_require = {
    'tests': tests_require,
    'test': tests_require,
}

setup(
    name='ftw.sliderblock',
    version=version,
    description='An image slider block to be used on a content page '
                'powered by ftw.simplelayout',
    long_description=open('README.rst').read() + '\n' + open(
        os.path.join('docs', 'HISTORY.txt')).read(),

    # Get more strings from
    # http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords='ftw plone slider block',
    author='4teamwork AG',
    author_email='mailto:info@4teamwork.ch',
    maintainer=maintainer,
    url='https://github.com/4teamwork/ftw.sliderblock',
    license='GPL2',

    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['ftw', ],
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'ftw.simplelayout [contenttypes] >= 1.22.0',
        'ftw.slider >= 3.1.5',
        'ftw.upgrade',
        'setuptools',
        'plone.api',
        'plone.dexterity',
        'plone.app.dexterity',
        'plone.app.registry',
        'Plone',
    ],

    tests_require=tests_require,
    extras_require=extras_require,

    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
