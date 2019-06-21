import setuptools

setuptools.setup(
    name="user-sdk",
    version="0.0.27",
    description="Interface for user auth/profile backend",
    url="https://github.com/shuttl-tech/user_sdk",
    author="Shuttl",
    author_email="paul.kuruvilla@shuttl.com",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests"],
    extras_require={
        "test": ["pytest", "pytest-runner", "pytest-cov", "pytest-pep8", "responses"]
    },
)
