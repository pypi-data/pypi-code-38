from setuptools import setup, find_packages
setup(
    name='pi-plates',
    version='5.12',
    license='BSD',
    author='Jerry Wasinger, WallyWare, inc.',
    author_email='support@pi-plates.com',
    keywords = "pi-plates,data acquisition,raspberry pi, relays, motors, temperature sensing",
    url='https://www.pi-plates.com',
    long_description="README.txt",
    packages=['piplates'],
    include_package_data=True,
    package_data={'' : ['*.txt']},
    description="Pi-Plates library setup",
)