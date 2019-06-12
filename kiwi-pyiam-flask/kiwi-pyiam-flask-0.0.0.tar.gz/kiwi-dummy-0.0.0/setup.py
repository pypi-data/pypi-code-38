from setuptools import setup

setup(
    name = 'kiwi-dummy',
    version = '0.0.0',
    description = 'This is a dummy package.',
)

raise RuntimeError("This is a dummy package that was never ment to be actually installed. Please contact platform(at)kiwi.com.")

