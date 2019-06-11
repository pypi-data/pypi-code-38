try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="preserves",
    version="0.0.5",
    author="Tony Garnock-Jones",
    author_email="tonyg@leastfixedpoint.com",
    license="GNU General Public License v3 or later (GPLv3+)",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
    ],
    packages=["preserves"],
    url="https://gitlab.com/tonyg/preserves",
    description="Experimental data serialization format",
    install_requires=[],
    python_requires=">=3.6, <4",
)
