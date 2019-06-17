import setuptools
import re

# version number from the class
with open("logo.py", "r") as ftt:
    readftt = ftt.readlines()

vers = re.compile(r'[0-9.]{1,10} ?[a-zA-Z]{0,8}')
for i in readftt:
    if "Version" in i:
        version = ",".join(re.findall(vers, i))
        version = version.replace(",", "")

# Readme from the README.md
with open("README.md", "r") as fh:
    long_description = fh.read()
long_description += "\n\nCHANGES\n\n"
# Readme adding CHANGES
with open("CHANGES", "r") as fh:
    long_desc_changes = fh.read()
long_desc_changes = str.replace(long_desc_changes, "\n", "\n\n")
long_description += long_desc_changes

setuptools.setup(
    name="french-logo",
    version=version,
    author="Robert Sebille",
    author_email="robert@sebille.name",
    maintainer = 'Robert Sebille',
    maintainer_email = 'robert@sebille.name',
    description="french-logo retourne un substitut de primitives logo \
    en français, basées sur le module turtle. Elle comporte également une \
    primitive repete récursive (absente du module turtle)",
    license="GNU GPL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://framagit.org/zenjo/timetime/wikis/home",
    download_url = 'https://framagit.org/zenjo/timetime/tree/master',
    keywords='runtime time tracking software development',
    #packages=setuptools.find_packages(),
    py_modules = ['logo', 'logo_demo'],
    #packages = ['film'],
    #package_data={
    #    'film': ['frame/*', 'frames/*'],
    #},
    #data_files = [('frame',['frame/poursuiteic', 'frame/poursuiteci', 'frame/roflflyingmoto']),
    #              ('frames',['frames/bon00', 'frames/bon10', 'frames/bon20', 'frames/bon30'])],
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: OS Independent",
    ],
)
