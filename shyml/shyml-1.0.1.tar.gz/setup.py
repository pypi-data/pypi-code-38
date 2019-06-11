from setuptools import setup

setup(
    name='shyml',
    version='1.0.1',
    url='https://yourlabs.io/oss/shyml',
    setup_requires='setupmeta',
    keywords='automation cli',
    python_requires='>=3',
    include_package_data=True,
    extras_require={
        'test': [
            'pytest',
            'pytest-cov',
        ],
    }
)
