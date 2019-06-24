from setuptools import setup, find_packages

setup(
    name='odoo-addon-manager',
    description='A tool to install and update odoo addons',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    version='0.1.1',
    author='e-COSI',
    author_email='tech.odoo@e-cosi.com',
    packages=find_packages(),
    py_modules=['oam'],
    url='https://gitlab.com/e-cosi/odoo/oam',
    repository='https://gitlab.com/e-cosi/odoo/oam',
    keywords=['odoo', 'module', 'addon'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)'
    ],
    install_requires=[
        'Click>=7.0',
        'callable-pip>=1.0.0',
        'fs>=2.4.4',
        'packaging>=19.0',
        'PyYAML>=5.1',
        'pygit2>=0.27.4',
    ],
    entry_points='''
        [console_scripts]
        oam=oam:cli
    ''',
)
