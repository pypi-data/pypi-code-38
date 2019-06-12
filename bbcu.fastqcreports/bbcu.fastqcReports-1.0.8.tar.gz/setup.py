from setuptools import setup, find_packages

with open('VERSION.txt', 'r') as version_file:
    version = version_file.read().strip()

requires = ['jinja2', 'BeautifulSoup4', 'matplotlib', 'bbcu.bioutils']

setup(
    name='bbcu.fastqcReports',
    version=version,
    author='Refael Kohen, Ophir Tal',
    author_email='refael.kohen@weizmann.ac.il, ophir.tal@weizmann.ac.il',
    packages=find_packages(),
    scripts=[
        'scripts/run-fastqc-report.py',
        'scripts/run-fastqc-report-table.py',
    ],
    description='Create summary of FastQC output in html file',
    long_description=open('README.txt').read(),
    install_requires=requires,
    tests_require=requires + ['nose'],
    include_package_data=True,
    test_suite='nose.collector',
)
