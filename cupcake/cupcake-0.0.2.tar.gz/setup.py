# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cupcake']

package_data = \
{'': ['*']}

install_requires = \
['cached-property>=1.5,<2.0',
 'click>=7.0,<8.0',
 'cmakelists_parsing>=0.3.1,<0.4.0',
 'conan>=1.15,<2.0',
 'dataclasses>=0.6.0,<0.7.0',
 'semantic_version>=2.6,<3.0',
 'toolz>=0.9.0,<0.10.0']

extras_require = \
{'docs': ['sphinx>=1.8,<2.0',
          'sphinx_rtd_theme>=0.4.3,<0.5.0',
          'toml>=0.10.0,<0.11.0']}

entry_points = \
{'console_scripts': ['cupcake = cupcake.main:main']}

setup_kwargs = {
    'name': 'cupcake',
    'version': '0.0.2',
    'description': 'Make C++ a piece of cake.',
    'long_description': '.. start-include\n\n=======\ncupcake\n=======\n\nMake C++ a piece of cake.\n\n.. image:: https://travis-ci.org/thejohnfreeman/cupcake.svg?branch=master\n   :target: https://travis-ci.org/thejohnfreeman/cupcake\n   :alt: Build status\n\n.. image:: https://readthedocs.org/projects/cupcake/badge/?version=latest\n   :target: https://cupcake.readthedocs.io/\n   :alt: Documentation status\n\n.. image:: https://img.shields.io/pypi/v/cupcake.svg\n   :target: https://pypi.org/project/cupcake/\n   :alt: Latest PyPI version\n\n.. image:: https://img.shields.io/pypi/pyversions/cupcake.svg\n   :target: https://pypi.org/project/cupcake/\n   :alt: Python versions supported\n\nCupcake is a thin layer over CMake_ and Conan_ that tries to offer\na better user experience in the style of Yarn_ or Poetry_.\n\n.. _CMake: https://cmake.org/cmake/help/latest/manual/cmake.1.html\n.. _Conan: https://docs.conan.io/\n.. _Yarn: https://yarnpkg.com/en/\n.. _Poetry: https://poetry.eustace.io/\n\n\nAudience\n========\n\nTo use this tool, your C++ project must fit a certain profile and follow some\nconventions. The profile is what I call a **basic C++ project**:\n\n- A **name** that is a valid C++ identifier.\n- Zero or more **public dependencies**. These may be runtime dependencies of\n  the library or executables, or they may be build time dependencies of the\n  public headers. Users must install the public dependencies when they install\n  the project.\n- Some **public headers** nested under a directory named after the project.\n- One **library**, named after the project, that can be linked statically or\n  dynamically (with no other options). The library depends on the public\n  headers and the public dependencies.\n- Zero or more **executables** that depend on the public headers, the library,\n  and the public dependencies.\n- Zero or more **private dependencies**. These are often test frameworks.\n  Developers working on the library expect them to be installed, but users of\n  the library do not.\n- Zero or more **tests** that depend on the public headers, the library, the\n  public dependencies, and the private dependencies.\n\nThe conventions are popular in the community and seem to be considered__\nbest__ practices__:\n\n.. __: https://www.youtube.com/watch?v=eC9-iRN2b04\n.. __: https://pabloariasal.github.io/2018/02/19/its-time-to-do-cmake-right/\n.. __: https://unclejimbo.github.io/2018/06/08/Modern-CMake-for-Library-Developers/\n\n- The project is built and installed with **CMake** [#]_.\n- The project uses **semantic versioning**.\n- The project installs itself relative to a **prefix**. Public headers are\n  installed in ``include/``; static and dynamic libraries are installed in\n  ``lib/``; executables are installed in ``bin/``.\n- The project installs a `CMake package configuration file`__ that exports\n  a target for the library. The target is named after the project, and it is\n  scoped within a namespace named after the project. Dependents link against\n  that target with the **same syntax** whether it was installed with CMake or\n  with Conan.\n\n.. __: https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html#package-configuration-file\n\n\nCommands\n========\n\n``package``\n-----------\n\nThis abstracts the ``conan create`` `↗️`__ command. It:\n\n.. __: https://docs.conan.io/en/latest/reference/commands/creator/create.html\n\n- Copies a Conan recipe for your project to your local Conan cache, a la\n  ``conan export`` `↗️`__.\n\n   .. __: https://docs.conan.io/en/latest/reference/commands/creator/export.html\n\n- Builds the recipe for your current settings (CPU architecture, operating\n  system, compiler) and the ``Release`` build type, a la ``conan install``\n  `↗️`__.\n\n   .. __: https://docs.conan.io/en/latest/reference/commands/consumer/install.html\n\n- Configures and builds an example that depends on your project as a test of\n  its packaging, a la ``conan\n  test`` `↗️`__. That example must reside in the ``example/`` directory of your\n  project with a ``CMakeLists.txt`` that looks like this:\n\n   .. __: https://docs.conan.io/en/latest/reference/commands/creator/test.html\n\n   .. code-block:: cmake\n\n      add_executable(example example.cpp)\n      target_link_libraries(example ${PROJECT_NAME}::${PROJECT_NAME})\n\n  .. TODO: example.cpp in place of example/ directory.\n\n\nEtymology\n=========\n\nI love Make_, but it\'s just not cross-platform. Just about every other\nsingle letter prefix of "-ake" is taken, including the obvious candidate for\nC++ (but stolen by C#), Cake_. From there, it\'s a small step to Cppcake,\nwhich needs an easy pronunciation. "Cupcake" works. I prefer names to be\nspelled with an unambiguous pronunciation so that readers are not left\nconfused, so I might as well name the tool Cupcake. A brief `Google\nsearch`__ appears to confirm\nthe name is unclaimed in the C++ community.\n\n.. _Make: https://www.gnu.org/software/make/\n.. _Cake: https://cakebuild.net/\n.. __: https://www.google.com/search?q=c%2B%2B+cupcake\n\n\n.. [#] CMake likes to remind everyone that it is a build system *generator*,\n   not a build system, but it is reaching a level of abstraction that lets\n   us think of it as a cross-platform build system.\n\n.. end-include\n',
    'author': 'John Freeman',
    'author_email': 'jfreeman08@gmail.com',
    'url': 'https://github.com/thejohnfreeman/cupcake/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6-dev,<4.0',
}


setup(**setup_kwargs)
