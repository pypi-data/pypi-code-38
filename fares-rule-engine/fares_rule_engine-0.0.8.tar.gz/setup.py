from setuptools import setup, find_packages

setup(
    name="fares_rule_engine",
    version="0.0.8",
    author="Noob Dev",
    author_email="author@example.com",
    description="Fares rule engine",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "py_rule_engine"],
    extras_require={
        "test": ["pytest", "pytest-runner", "pytest-cov", "pytest-pep8"],
        "dev": ["flake8"],
    },
)
