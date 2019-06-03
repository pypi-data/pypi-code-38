import setuptools

VERSION=open('version.txt').read().strip()
setuptools.setup(
    name='pytest_mproc',
    version=VERSION,
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    entry_points={
       "pytest11": ["name_of_plugin = pytest_mproc.plugin"],
    },
    classifiers=["Framework :: Pytest"],
    url='https://github.com/jrusnakli/pytest_mpdist',
    download_url="https://github.com/jrusnakli/pytest_mpdist/dist/%s" % VERSION,
)
