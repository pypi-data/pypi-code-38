from setuptools import find_packages, setup
import six

avro_version = "avro >= 1.7.6"
if six.PY3:
    avro_version = "avro-python3 >= 1.7.6"

setup(
    name = "fastscoredeploy",
    description = "FastScore Deploy",
    version = "1.10.1",
    packages = find_packages(),
    use_2to3=True,
    author="Open Data Group",
    author_email="support@opendatagroup.com",
    install_requires = [
        "iso8601>=0.1.11",
        "PyYAML>=3.11",
        "requests>=2.11.1",
        "tabulate>=0.7.5",
        "websocket-client>=0.37.0",
        avro_version,
        "fastavro",
        "six",
        "numpy >= 1.6.1",
        "pandas >= 0.19.0",
        "fastscore"
    ],
    test_suite="test",
    tests_require=[
        "iso8601>=0.1.11",
        "PyYAML>=3.11",
        "requests>=2.11.1",
        "tabulate>=0.7.5",
        "websocket-client>=0.37.0",
        avro_version,
        "six",
        "numpy >= 1.6.1",
        "pandas >= 0.19.0",
        "fastscore",
        "mock"
    ]
)
