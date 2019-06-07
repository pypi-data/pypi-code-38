import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='easy_multip',
    version='0.2.3',
    packages=['easy_multip'],
    license='MIT',
    author='Zach Bateman',
    description='Easy Python multiprocessing',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/zachbateman/easy_multip.git',
    download_url='https://github.com/zachbateman/easy_multip/archive/v_0.2.3.tar.gz',
    keywords=['MULTIPROCESSING', 'SIMPLE', 'EASY', 'PARALLEL'],
    install_requires=['tqdm'],
    classifiers=['Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   ]
)
