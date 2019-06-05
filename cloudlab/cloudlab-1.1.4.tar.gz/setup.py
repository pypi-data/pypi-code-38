import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='cloudlab',
    version='1.1.4',
    author='Randy May',
    description='A tool for quickly provisioning environments on AWS for use with classes and performance labs.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/wrmay/cloudlab',
    packages=setuptools.find_packages(),
    package_data={ '': ['plans/**/*', 'cloudlab_config.yaml']},
    entry_points = {
        'console_scripts' : ['cloudlab=cloudlab.commandline:run']
    },
    license='MIT',
    install_requires=['tplate>=1.0.3','awscli>=1.16','setuptools>=41.0.1', 'PyYaml<=3.13']
)
