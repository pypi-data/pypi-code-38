import setuptools

with open("README.md", "r") as fh:
    for line in fh.readlines():
        if "Version" in line:
            version = line.split(":")[1].strip().rstrip('\n')

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'requests',
    'urllib3',
    'cython',
    'pyyaml',
    'boto3',
    'docker',
    'psycopg2-binary',
    'ddls3utils',
    'virtualenv',
    'psutil',
    'dcdataset'
]

print("Build: dcworker")
print(". Version: {}".format(version))
print(". Requirements: {}".format(requirements))

setuptools.setup(
    name="dcworker",
    version=version,
    author="YL & SW",
    author_email = 'deepcluster.io@gmail.com',
    description="DeepCluster worker package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=['*.test', '*.test.*', 'test.*', 'test', 'data_container', ]),
    entry_points={
        'console_scripts': [
            'dcworker=main.worker_main:main',
        ],
    },
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)