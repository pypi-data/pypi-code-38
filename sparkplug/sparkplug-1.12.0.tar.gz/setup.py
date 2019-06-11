from setuptools import setup, find_packages
import os.path as p

with open(p.join(p.dirname(__file__), 'requirements.txt'), 'r') as reqs:
    install_requires = [line.strip() for line in reqs]

with open(p.join(p.dirname(__file__), 'requirements-dev.txt'), 'r') as reqs:
    tests_require = [
        line.strip()
        for line in reqs
        if not line.startswith('-r')]

with open(p.join(p.dirname(__file__), 'README.md'), 'r') as f:
    long_description = f.read()

setup(
    name='sparkplug',
    version='1.12.0',
    maintainer='FreshBooks',
    maintainer_email='dev@freshbooks.com',
    url='https://github.com/freshbooks/sparkplug/',
    download_url='https://pypi.python.org/pypi/sparkplug/',
    description='An AMQP message consumer daemon',
    long_description=long_description,
    long_description_content_type="text/markdown",

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Topic :: Utilities'
    ],

    packages=find_packages(exclude=['*.test', '*.test.*']),

    tests_require=tests_require,
    install_requires=install_requires,

    entry_points={
        'console_scripts': [
            'sparkplug = sparkplug.cli:main'
        ],
        'sparkplug.connectors': [
            'connection = sparkplug.config.connection:AMQPConnector'
        ],
        'sparkplug.configurers': [
            'time_reporter = sparkplug.config.timereporter:TimeReporterConfigurer',
            'queue = sparkplug.config.queue:QueueConfigurer',
            'exchange = sparkplug.config.exchange:ExchangeConfigurer',
            'binding = sparkplug.config.binding:BindingConfigurer',
            'consumer = sparkplug.config.consumer:ConsumerConfigurer',
        ],
        'sparkplug.consumers': [
            'echo = sparkplug.examples:EchoConsumer',
            'broken = sparkplug.examples:Broken',
            'heartbeat = sparkplug.test.test_heartbeat.heartbeat_consumer:HeartbeatConsumer'
        ],
        'sparkplug.time_reporters' : [
            'logger = sparkplug.timereporters.logger:Logger',
            'statsd = sparkplug.timereporters.statsd:Statsd',
        ]
    },

    test_suite='nose.collector'
)
