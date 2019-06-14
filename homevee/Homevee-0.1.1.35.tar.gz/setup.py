import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Homevee",
    version="0.1.1.35",
    author="Homevee",
    author_email="support@Homevee.de",
    description="Dein neues Smarthome-System!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Homevee/Homevee",
    entry_points = {
        'console_scripts': ['Homevee=Homevee.CommandLine:main'],
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        #'babel',
        'packaging',
        'python-dateutil',
        'pyOpenSSL',
        #'tensorflow',
        #'tensorflow-gpu',
        'pymax',
        'paho-mqtt',
        'Pillow',
		'passlib',
		'numpy',
        'azure-iothub-device-client',
        'flask',
        'psutil'
    ]
)

#Commands to build
#sudo apt-get install python3-pip python3-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg8-dev zlib1g-dev -y
#pip install --upgrade setuptools wheel twine
