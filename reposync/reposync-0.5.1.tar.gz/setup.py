import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="reposync",
    version="0.5.1",
    description="reposync helps you manage a lot of git repositories.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devinalvaro/reposync",
    author="Devin Alvaro",
    author_email="devin.alvaro@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    project_urls={
        "Documentation": "https://github.com/devinalvaro/reposync",
        "Source": "https://github.com/devinalvaro/reposync",
        "Tracker": "https://github.com/devinalvaro/reposync/issues",
    },
    install_requires=["fire", "gitpython", "pyaml"],
    python_requires=">=3",
    packages=setuptools.find_packages(),
    scripts=["reposync/scripts/reposync"],
)
