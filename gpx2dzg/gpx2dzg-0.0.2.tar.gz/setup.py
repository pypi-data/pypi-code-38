import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="gpx2dzg",
    version="0.0.2",
    author="Ian Nesbitt",
    author_email="ian.nesbitt@gmail.com",
    license='GPLv3',
    description="convert GPX files to GSSI's proprietary DZG format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iannesbitt/gpx2dzg",
    packages=setuptools.find_packages(),
    install_requires=['gpxpy', 'geomag', 'pynmea2', 'readgssi'],
    entry_points='''
        [console_scripts]
        gpx2dzg=gpx2dzg.gpx2dzg:main
    ''',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
        "Natural Language :: English",
        "Development Status :: 4 - Beta",
    ],
)
