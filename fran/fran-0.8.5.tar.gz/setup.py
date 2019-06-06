import setuptools
from pathlib import Path

here = Path(__file__).absolute().parent
package = here / "fran"

with open(here / "README.md") as f:
    long_description = f.read()

setuptools.setup(
    name="fran",
    version="0.8.5",
    packages=["fran"],
    install_requires=[
        "imageio>=2.5.0",
        "pygame>=1.9.5",
        "pandas>=0.24.2",
        "numpy>=1.16.2",
        "scikit-image>=0.15.0",
        "toml>=0.10.0",
    ],
    tests_require=["pytest>=4.6.2"],
    package_data={"fran": ["config.toml", "controls.txt"]},
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "fran = fran.__main__:main",
            "frame_annotator = fran.__main__:main",
            "fran-rename = fran.rename:main",
        ]
    },
    url="https://github.com/clbarnes/frame_annotator",
    license="MIT",
    author="Chris L. Barnes",
    author_email="barnesc@janelia.hhmi.org",
    description="Annotate frames of a multiTIFF video",
)
