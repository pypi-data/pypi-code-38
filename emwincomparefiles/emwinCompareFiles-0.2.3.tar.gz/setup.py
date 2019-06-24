import setuptools

setuptools.setup(
    name='emwinCompareFiles',
    version='0.2.3',
    author='Katie D\'Adamo',
    author_email='katherine.dadamo@noaa.gov',
    description='EMWIN Latency Comparison.',
    url='http://pypi.org/project/emwinCompareFiles/',
    packages=setuptools.find_packages(),
    license='LICENSE.txt',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.1",
        "caldav == 0.1.4",
    ],
)
