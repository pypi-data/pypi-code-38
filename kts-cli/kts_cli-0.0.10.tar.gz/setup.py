import setuptools

with open('VERSION', 'r') as f:
    VERSION = int(f.read().strip())

VERSION += 1

with open('VERSION', 'w') as f:
    f.write(str(VERSION))

setuptools.setup(
    name="kts_cli",
    version=f"0.0.{VERSION}",
    author="Nikita Konodyuk",
    author_email="konodyuk@gmail.com",
    description="Command line interface for kts package",
    url="https://github.com/konodyuk/kts-cli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": ['kts=kts_cli:run']
    }
)
