import setuptools

setuptools.setup(
    name="user-sdk",
    version="0.0.26",
    author="Noob Dev",
    author_email="author@example.com",
    description="Interface for user auth/profile backend",
    long_description="This is a very long description, like very wrong.",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests"],
    extras_require={"test": ["pytest", "pytest-runner", "pytest-cov", "pytest-pep8", "responses"]},
)
