import pathlib
import setuptools


def read(*args):
    file_path = pathlib.Path(__file__).parent.joinpath(*args)
    return file_path.read_text("utf-8")


setuptools.setup(
    name="pytest-pings",
    description="🦊 The pytest plugin for Firefox Telemetry 📊",
    version="0.1.0",
    author="Benjamin Forehand Jr, Raphael Pierzina",
    maintainer="Benjamin Forehand Jr, Raphael Pierzina",
    license="Mozilla Public License 2.0",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/hackebrot/pytest-pings",
    project_urls={
        "Repository": "https://github.com/hackebrot/pytest-pings",
        "Issues": "https://github.com/hackebrot/pytest-pings/issues",
    },
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=["pytest>=5.0.0", "pytest-aiohttp>=0.3.0"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
    ],
    entry_points={"pytest11": ["pings = pytest_pings.plugin"]},
    keywords=["pytest", "firefox telemetry"],
)
