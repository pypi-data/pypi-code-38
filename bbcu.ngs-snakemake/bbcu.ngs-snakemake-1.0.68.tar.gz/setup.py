from setuptools import setup, find_packages

with open('VERSION.txt', 'r') as version_file:
    version = version_file.read().strip()

requires = ['numpy==1.14.0', 'pandas==0.19.2', 'pysam==0.10.0', 'HTSeq==0.9.1', 'bbcu.fastqcReports']

setup(
    name='bbcu.ngs-snakemake',
    version=version,
    author='Refael Kohen',
    author_email='refael.kohen@weizmann.ac.il',
    packages=find_packages(),
    scripts=[
        'scripts/CorrectCounts.py',
        'scripts/ExtractBCSR.py',
        'scripts/gtfUTRutils.py',
        'scripts/gtfUTRutils_oldVersion.py',
        'scripts/MarkDuplicatesUMIbyGene.py',
        'scripts/MoveBC.py',
        'scripts/PrepareFilesToReport.py',
        'scripts/ReportsCounts.py',
        'scripts/UtilDeDup.py',
        'scripts/SinglecellUtils.py',
    ],
    description='Snakemake pipeline for Mars-seq and RNA-seq.',
    long_description=open('README.txt').read(),
    install_requires=requires,
    tests_require=requires + ['nose'],
    include_package_data=True,
    test_suite='nose.collector',
)
