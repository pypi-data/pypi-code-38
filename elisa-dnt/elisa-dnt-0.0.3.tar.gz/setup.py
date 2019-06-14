from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='elisa-dnt',
    version='0.0.3',
    packages=['elisa_dnt'],
    url='https://github.com/ChenghaoMou/elisa-dnt',
    license='',
    author='chenghaomou',
    author_email='chengham@isi.edu',
    description='Do Not Translate for machine translation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'emoji',
        'regex',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3.7',  # Specify which pyhton versions that you want to support
    ],
)
