from setuptools import find_packages, setup

setup(
    name='dvalidator',
    version='0.1',
    description='dvalidator validation attributes',
    license='MIT',
    author='Vlasov Sergei',
    author_email='kakabara@outlook.com',
    url='https://github.com/kakabara/dvalidator',
    packages=find_packages(),
    install_requires=[
        'ipaddress==1.0.22',
        'jsonschema==3.0.1'
    ]
)
