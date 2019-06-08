import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="factorio-changelog-creator",
    version="1.1.1",
    entry_points={
        "console_scripts": [
            "factorio-changelog-creator = factorio_changelog_creator.command_line:main"
        ]
    },
    author="Roang_zero1",
    author_email="lucas@brandstaetter.tech",
    description="A script to generate multiple factorio changelog formats.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Roang-zero1/factorio-changelog-creator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

