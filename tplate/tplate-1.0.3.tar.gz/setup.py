import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='tplate',
    version='1.0.3',
    author='Randy May',
    description='A project templating tool that based on Jina2',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/wrmay/tplate',
    packages=setuptools.find_packages(),
    entry_points = {
        'console_scripts' : ['tplate=tplate.commandline:run']
    },
    license='MIT',
    install_requires=['PyYaml>=3.13','Jinja2>=2.10.1']
)
