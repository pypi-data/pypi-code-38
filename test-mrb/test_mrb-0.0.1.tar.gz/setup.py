from setuptools import setup, find_packages
from setuptools.command.install import install

import test_mrb

with open('readme.md', 'r') as f:
    long_description = f.read()


class CustomInstall(install):
    def run(self):
        print('CUSTOM INSTALL SCRIPT!!!!!!')
        test_mrb.configure.main()
        install.run(self)


setup(
    name=test_mrb.__NAME__,
    packages=find_packages(),
    version=test_mrb.__VERSION__,
    author=test_mrb.__AUTHOR__,
    author_email=test_mrb.__AUTHOR_EMAIL__,
    description=test_mrb.__DESCRIPTION__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=test_mrb.__LICENSE__,
    url=test_mrb.__HOMEPAGE__,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'test_mrb-configure=test_mrb.configure:main',
        ]
    },
    cmdclass={
        'install': CustomInstall,
    },
)
