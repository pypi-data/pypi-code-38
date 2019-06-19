import os.path
from setuptools import setup, find_packages

package_dir = os.path.abspath(os.path.dirname(__file__))
version_file = os.path.join(package_dir, "version")
with open(version_file) as version_file_handle:
    version = version_file_handle.read()

setup(
    name = "falcors",
    version = version,
    description = "Falcon CORS middlware",
    package_dir = {"":"src"},
    packages = find_packages("src"),
    install_requires=["falcon"],
    author = 'Gnucoop',
    author_email = 'dev@gnucoop.com',
    url = 'https://github.com/gnucoop/falcors',
    download_url = 'https://github.com/gnucoop/falcors/archive/2.0.0.zip',
    keywords = ['falcon', 'cors', 'http'],
    classifiers = []
)
