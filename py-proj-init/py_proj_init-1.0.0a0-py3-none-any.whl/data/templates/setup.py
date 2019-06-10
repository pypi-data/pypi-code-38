import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as f:
    install_requires = [req for req in f.read().split('\n') if req]


setuptools.setup(
    name="{package_name}",
    version="0.0.1",
    author="author",
    author_email="author@email",
    description="Project short description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/project/repository",
    packages=setuptools.find_packages(),
    python_requires='>=3.2',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            '{namespace} = {package_name}.__main__:main',
        ]
    },
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
