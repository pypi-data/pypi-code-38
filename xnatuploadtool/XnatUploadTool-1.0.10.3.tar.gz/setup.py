from setuptools import setup

setup(
    name='XnatUploadTool',
    version='1.0.10.3',
    description='Tool for assisting in uploading data directly to xnat imaging research platform (xnat.org)',
    packages=['XnatUploadTool'],
    scripts=['scripts/xnat-uploader'],
    author='Brian Holt',
    author_email='brian@radiologics.com',
    license='BSD 3-Clause License',
    keywords='xnat',
    python_requires='>=2.6',
    classifiers=[
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2',
    ],
    url='https://bitbucket.org/radiologics/XnatUploadTool',
    install_requires=[
        "requests>=2.18.4",
        "EasyProcess>=0.2.3",
        "pyunpack>=0.1.2",
        "mime>=0.1.0",
        "pydicom >= 1.0.0",
        "patool>=1.12",
        "python-magic>=0.4.15",
        "pathos>=0.2.1",
        "ConfigArgParse>=0.13.0",
        "ConfigParser"
    ]
)
