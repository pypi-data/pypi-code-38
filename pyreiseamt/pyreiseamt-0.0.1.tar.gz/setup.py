import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyreiseamt",
    version="0.0.1",
    author="Joshua Hruzik",
    author_email="joshua.hruzik@gmail.com",
    description="Package to crawl country information of German Foreign Office",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    zip_safe=False,
    package_data = {
            "" : ["*.obj"]
            },
    url="https://github.com/Jhruzik/pyreiseamt",
    packages=setuptools.find_packages(),
    install_requires=["requests", "bs4", "lxml"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Topic :: Internet :: WWW/HTTP"
    ],
    entry_points = {
            "console_scripts" : [
                    "pyreiseamt = pyreiseamt.__main__:main"
                    ]
            }
)
