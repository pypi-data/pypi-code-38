import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = __import__('serverchecks').__version__
packages = setuptools.find_packages()
print(packages)

setuptools.setup(
    name="serverchecks",
    version=version,
    author="Pawel Krawczyk",
    author_email="pawel.krawczyk@hush.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/kravietz/serverchecks",
    keywords='network ping check test dns url availability imap pop3 smtp http dnssec',
    packages=packages,
    install_requires=('pyyaml','yamale'),
    extras_require={
        'dnssec': ('pycryptodomex', 'ecdsa', 'dnspython'),
        'dns': ('dnspython',),
        'xmpp': ('aioxmpp',),
        'matrix': ('matrix_client',),
        'telegram': ('telethon',),
    },
    entry_points={'console_scripts': ('serverchecks = serverchecks.main:command',)},
    package_data={'': ['config.yaml']},
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
