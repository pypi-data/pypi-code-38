from setuptools import setup

from stos import __version__

with open("README.rst", "rt") as f:
    readme = f.read()

setup(
    name="StosPy",
    version=__version__,
    # project_urls={
    #     "Documentation": "http://.../docs/",
    #     "Code": "https://github.com/...",
    #     "Issue tracker": "https://github.com/.../issues"
    # }
    license="GPLv3",
    author="Alex Barcelo",
    author_email="alex.barcelo@bsc.es",
    maintainer="Workflows and Distributed Computing - BSC",
    maintainer_email="distributed_computing@bsc.es",
    description="Smart and Transparent Object Swapper for Python",
    long_description=readme,
    packages=["stos"],
    install_requires=[
        "psutil",
        "readerwriterlock",
    ],
    python_requires=">=3.4",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
    ],
)
