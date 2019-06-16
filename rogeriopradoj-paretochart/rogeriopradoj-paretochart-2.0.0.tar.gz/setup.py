import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='rogeriopradoj-paretochart',
    version='2.0.0',
    author='Rogerio Prado de Jesus',
    author_email='rogeriopradoj@gmail.com',
    description="Pareto chart for python (similar to Matlab's, but much more flexible)  - Fork from @tintrinh",
    url='https://github.com/rogeriopradoj/rogeriopradoj-paretochart',
    download_url='https://github.com/rogeriopradoj/rogeriopradoj-paretochart/archive/2.0.0.tar.gz',
    license='BSD License',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    install_requires=['matplotlib'],
    packages=[
        'paretochart'
    ],
    keywords=[
        'rogeriopradoj',
        'matplotlib',
        'pareto',
        'chart',
        'plot',
        'quality',
        'economics',
        'manufacturing'
        ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Customer Service',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Office/Business',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        ]
    )
