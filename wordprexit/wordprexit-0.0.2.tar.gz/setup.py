"""
Convert a Wordpress WXR export to a Hugo static site.
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wordprexit",
    version="0.0.2",
    url="https://github.com/2n3906/wordprexit",
    license='MIT',
    author="Scott Johnston",
    author_email="sjohnston@alum.mit.edu",
    description="Convert a Wordpress WXR export to a Hugo static site.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        "beautifulsoup4",
        "click",
        "html2text",
        "python-dateutil",
        "pytz",
        "requests",
        "ruamel.yaml",
        "tzlocal",
    ],
    entry_points={
        'console_scripts': [
            'wordprexit = wordprexit.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ]
)
