from setuptools import setup

setup(
    name='masonite-essentials',
    packages=[
        'masonite.contrib',
        'masonite.contrib.essentials',
        'masonite.contrib.essentials.helpers',
        'masonite.contrib.essentials.helpers.views',
        'masonite.contrib.essentials.middleware',
        'masonite.contrib.essentials.providers',
    ],
    version='0.0.2',
    install_requires=[
        'masonite>=2.1,<2.3'
    ],
    extras_require={
        'hashids': ['hashids>=1.2,<1.3']
    },
    package_dir={'': 'src'},
    description='Essential Features for Masonite',
    author='Joseph Mancuso',
    author_email='joe@masoniteproject.com',
    url='https://github.com/MasoniteFramework/essentials',
    keywords=['masonite', 'python web framework', 'python3'],
    licence='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'Operating System :: OS Independent',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',

        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data=True,
)
