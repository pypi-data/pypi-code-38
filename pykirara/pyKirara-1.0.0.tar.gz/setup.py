import setuptools

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open("README.md") as f:
    readme = f.read()

setuptools.setup(name='pyKirara',
    author='EthanSk13s',
    url='https://github.com/EthanSk13s/pyKirara',
    project_urls={
    "Documentation": "https://pykirara.readthedocs.io/"
    },
    version='1.0.0',
    packages=['pyKirara'],
    license='MIT',
    description='a Python wrapper for the starlight.kirara API',
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    python_requires='>=3.6',
    classifiers=[
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.6',
    'Topic :: Internet',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
    ]
)
