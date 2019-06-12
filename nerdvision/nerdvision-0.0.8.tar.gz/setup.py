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
        name = 'nerdvision',
        version = '0.0.8',
        description = 'The python nerd.vision agent, allowing real time debugging, any environment, any cloud.',
        long_description = 'To use this please view the docs at https://docs.nerd.vision/python/configuration/',
        author = '',
        author_email = '',
        license = 'https://www.nerd.vision/legal/agent-license',
        url = 'https://nerd.vision',
        scripts = [],
        packages = [
            'nerdvision',
            'nerdvision.settings',
            'nerdvision.models'
        ],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [
            'netifaces',
            'grpcio-tools',
            'nerdvision_grpc_api==1.0.0',
            'requests'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
