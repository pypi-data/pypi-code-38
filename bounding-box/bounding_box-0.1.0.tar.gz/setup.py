from setuptools import setup, find_packages

# install_requires = [
#     'pandas',
#     'pyarrow >= 0.12.1',
#     'tqdm >= 4.31.1',
# ]

install_requires = []

setup(
    name='bounding_box',
    version='0.1.0',

    python_requires='>=2.7',

    packages=find_packages(),
    include_package_data=True,

    author='Manu NALEPA',
    author_email='nalepae@gmail.com',
    description='A tool to plot pretty bounding boxes around objects.',
    long_description='See https://github.com/nalepae/bounding_box/tree/v1.0.0 for complete user guide.',
    url='https://github.com/nalepae/bounding_box',
    install_requires=install_requires,
    license='BSD',
)
