import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as f:
    install_requires = [req for req in f.read().split('\n') if req]


setuptools.setup(
    name="py_proj_init",
    version="1.0.0a",
    author="ZhenningLang",
    author_email="zhenninglang@163.com",
    description="Python3 project directory initializer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZhenningLang/py-proj-init",
    packages=setuptools.find_packages(),
    python_requires='>=3.2',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'py-proj-init = py_proj_init.__main__:main',
        ]
    },
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
