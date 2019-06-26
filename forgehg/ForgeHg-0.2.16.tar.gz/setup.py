from setuptools import setup
import sys, os

from forgehg.version import __version__

TOOL_DESCRIPTION = """ForgeHg enables an Allura installation to use the Mercurial
source code management system. Mercurial (Hg) is an open source distributed
version control system (DVCS) similar to git and written in Python.
"""

setup(name='ForgeHg',
      version=__version__,
      description="Mercurial (Hg) SCM support for Apache Allura",
      long_description=TOOL_DESCRIPTION,
      classifiers=[
        ## From http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: TurboGears',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
      ],
      keywords='Allura forge Mercurial Hg scm',
      author_email='dev@allura.apache.org',
      url='http://sourceforge.net/p/forgehg',
      license='GPLv2',
      packages=[
        'forgehg',
        'forgehg.model',
        'forgehg.templates'
      ],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # mercurial 3.2.3 starts giving UnicodeDecodeError from hfsignoreclean.
          # And later in 3.4 through 4.x UnicodeWarning: Unicode equal comparison...
          'mercurial < 3.2.3',
      ],
      entry_points="""
      [allura]
      Hg=forgehg.hg_main:ForgeHgApp

      [allura.timers]
      hg = forgehg.hg_main:hg_timers
      forgehg = forgehg.hg_main:forgehg_timers
      """,
      )
