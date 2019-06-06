import setuptools
from calligraphy import __version__ as VERSION

if __name__ == "__main__":
    setuptools.setup(
        name='dashboardspot',
        version=VERSION,
        author="Terrillo Walls",
        author_email="terrillo@terrillo.com",
        url="https://github.com/terrillo/dashboardspot-python",
        description="DashboardSpot pyhon library.",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        install_requires=[
            "requests"
        ],
        project_urls={
            "Bug Tracker": "https://github.com/terrillo/dashboardspot-python/issues",
            "Documentation": "https://github.com/terrillo/dashboardspot-python",
            "Source Code": "https://github.com/terrillo/dashboardspot-python",
        },
        python_requires=">=3.0.*",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ]
    )
