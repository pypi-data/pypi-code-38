try:
    from setuptools import setup, find_packages, Command
except ImportError:
    from distutils.core import setup, find_packages, Command

setup(
# A string corresponding the package author’s name
    author="Luis (Lugg) Gustavo",

    # A string corresponding the email address of the package author
    author_email="the.nonsocial@gmail.com",
    classifiers=[
        # Trove classifiers - Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers | https://pypi.org/classifiers/
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    description="A mirror package for pyrez. Please install that instead.",

    keywords=['pyrez', 'hirez', 'hi-rez', 'smite', 'paladins', 'realmapi', 'open-source', 'api', 'wrapper', 'library', 'python', 'api-wrapper', 'paladins-api', 'smitegame', 'smiteapi', 'realm-api', 'realm-royale', 'python3', 'python-3', 'python-3-6', 'async', 'asyncio'],
    license="MIT",
    long_description='*This is a mirror package!* It is recommended to install `pyrez` instead.',
    long_description_content_type='text/markdown; charset=UTF-8; variant=GFM', #https://guides.github.com/features/mastering-markdown/
    maintainer="Luis (Lugg) Gustavo",
    maintainer_email="the.nonsocial@gmail.com",

    # A string corresponding to distribution name of your package. This can be any name as long as only contains letters, numbers, _ , and -. It also must not already taken on pypi.org
    name="hirez.py",
    packages=find_packages(exclude=['docs', 'tests*', 'examples', '.gitignore', '.github', '.gitattributes', 'README.md']),# packages=[NAME]
    platforms = 'any',

    # A string corresponding to a version specifier (as defined in PEP 440) for the Python version, used to specify the Requires-Python defined in PEP 345.
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,<4', #python_requires='>=3.0, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, !=3.7.*, !=3.8.*',

    url="https://github.com/luissilva1044894/pyrez",

    # A string corresponding the version of this release
    version='0.0.0dev0',

    project_urls={
        'Documentation': 'https://pyrez.readthedocs.io/en/latest/',
        'Discord: Support Server': 'https://discord.gg/XkydRPS',
    },
)