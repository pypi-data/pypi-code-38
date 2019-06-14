from setuptools import setup

with open("VERSION.txt") as versionfile:
    version = versionfile.readline()
    print(version)
    setup(
        name="pandoc-compose",
        version=version,
        description="Create and run a fully configured pandoc command.",
        url="http://github.com/gfelbing/pandoc-compose",
        author="Georg Felbinger",
        author_email="gfelbing@github.com",
        license="GPLv3",
        packages=['pandoc_compose'],
        scripts=['bin/pandoc-compose'],
        zip_safe=False,
        install_requires=['argparse', 'pyyaml'],
        include_package_data=True
    )
