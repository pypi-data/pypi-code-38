from setuptools import setup, find_packages

import test_mrb
from test_mrb.configure.post_install import CustomInstall

setup(
    name=test_mrb.__NAME__,
    packages=find_packages(),
    version=test_mrb.__VERSION__,
    author=test_mrb.__AUTHOR__,
    author_email=test_mrb.__AUTHOR_EMAIL__,
    description=test_mrb.__DESCRIPTION__,
    long_description=open('readme.md', 'r').read(),
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
