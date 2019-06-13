import setuptools

setup = dict(
    name="Custom Accounts Django",
    version="0.1",
    author="Julian Kimmig",
    author_email="julian-kimmig@gmx.net",
    description="Cusstomizable Account app for Django",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    #py_modules=["django_websocket_server"],
    include_package_data=True,
    url="https://github.com/JulianKimmig/django_accounts",
     packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
if __name__ == "__main__":
    setuptools.setup(**setup)
