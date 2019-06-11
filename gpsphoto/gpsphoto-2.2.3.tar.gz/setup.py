import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='gpsphoto',
    version='2.2.3',
    author='Jess Williams',
    author_email='stripes.denomino@gmail.com',
    description=str("Returns, Modifies, or Removes GPS Data from Exif Data " +
            "in jpeg and tiff photos. Requires ExifRead, piexif, and PIL."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://www.jessgwiii.wordpress.com',
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        str("License :: OSI Approved :: GNU Lesser General Public License v3 " +
                "or later (LGPLv3+)"),
        "Operating System :: OS Independent",
    ),
)
