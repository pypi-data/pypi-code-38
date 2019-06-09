#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'dfmaps2',
        version = '1.2',
        description = 'Trabajo Final de grado Isabela San Jose, representacion de dataframes en mapas',
        long_description = 'Trabajo Final de grado Isabela San Jose,\n              representacion de dataframes en mapas',
        author = '',
        author_email = '',
        license = 'None',
        url = 'https://github.com/',
        scripts = ['scripts/hello-pybuilder'],
        packages = ['string_funcs'],
        namespace_packages = [],
        py_modules = ['helloworld'],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
