from setuptools import setup, find_packages

setup(
    name="sysstat",
    packages=find_packages(),
    version="0.1",
    author="Ilya_Yaruk",
    author_email="ilya_yaruk@epam.com",
    description="Script to collect PC usage statistics",
    license="MIT",
    install_requires=[
        'psutil'
    ],
    include_package_data=False
)
