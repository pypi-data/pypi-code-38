from setuptools import setup


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'skuidsphinx/VERSION'
    version = open(VERSION_FILE, 'r').read().strip()
    if version:
        return version
    else:
        raise RuntimeError('Unable to find version string in {0}'.format(VERSION_FILE))


setup(
    name='SkuidSphinxTheme',
    version=get_version(),
    description='Sphinx Theme for Skuid',
    long_description=open('README.rst').read(),
    url='https://github.com/skuid/SkuidSphinxTheme',
    author='Shannon Hale',
    author_email='shannon@skuid.com',
    keywords='skuid, documentation',
    classifiers=[
        'Topic :: Documentation :: Sphinx',
        'Framework :: Sphinx :: Theme',
    ],
    packages=['skuidsphinx'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'sphinx_themes': [
            'path=skuidsphinx:get_path',
        ]
    },
)
