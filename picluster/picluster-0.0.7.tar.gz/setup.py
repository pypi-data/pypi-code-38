# from setuptools import setup, find_packages

# setup(
#     name="dxl-picluster",
#     version="0.0.6",
#     description="Cluster utility library.",
#     url="https://github.com/tech-pi/dxcluster",
#     author="Hong Xiang",
#     author_email="hx.hongxiang@gmail.com",
#     license="MIT",
#     namespace_packages=["dxl"],
#     packages=find_packages("src/python"),
#     package_dir={"": "src/python"},
#     install_requires=[
#         "typing",
#         "networkx",
#         "apscheduler",
#         "arrow",
#         "fs",
#         "click",
#         "rx>=3.0.0a3",
#         "pyyaml",
#         "attrs",
#         "marshmallow>=3.0.0b16",
#         "requests",
#         "sqlalchemy",
#     ],
    #     entry_points="""
#             [console_scripts]
#             dxcluster=dxl.picluster.cli:cli
#       """,
#     scripts=[],
#     zip_safe=False,
# )



from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='picluster',
    version='0.0.7',
    description='A batch task utility.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tech-pi/PiCluster',
    author='Tsinglung.Tseng',
    author_email='tsinglung.tseng@gmail.com',

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='Batch compute tasks utility',
    packages=find_packages("src/python"),
    package_dir={"": "src/python"},
    python_requires='>=3.6',
    install_requires=[
        "typing",
        "rx>=3.0.0b4",
        "attrs",
        "marshmallow>=3.0.0b16",
        "requests",
        "sqlalchemy",
    ],
)