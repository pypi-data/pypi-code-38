from setuptools import setup

setup(
    name='elisa-dnt',
    version='0.0.1',
    packages=['elisa_dnt'],
    url='https://github.com/ChenghaoMou/elisa-dnt',
    license='',
    author='chenghaomou',
    author_email='chengham@isi.edu',
    description='Do Not Translate for machine translation',
    install_requires=[
        'emoji',
        'regex',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3.7',  # Specify which pyhton versions that you want to support
    ],
)
