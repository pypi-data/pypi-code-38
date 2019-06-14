from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='elisa-patch',
    version='0.3.2',
    packages=['elisa_patch'],
    url='https://github.com/ChenghaoMou/elisa-patch',
    license='',
    author='chenghaomou',
    author_email='chengham@isi.edu',
    description='Dictionary incorporation for machine translation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'unidecode',
        'emoji',
        'kenlm',
        'fuzzy',
        'scikit-learn',
        'pyxdameraulevenshtein',
        'pygtrie',
        'numpy'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3.7',  # Specify which pyhton versions that you want to support
    ],
)
