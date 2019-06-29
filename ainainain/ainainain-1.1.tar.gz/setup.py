from setuptools import setup, find_packages

NAME = "ainainain"
VERSION = "1.1"

packages = [
  "setuptools",
  "wheel",
  "python-dotenv==0.10.1",
  "docker==3.7.0",
  "requests-unixsocket==0.1.5",
  "click==7.0"
]

setup(
    package_data = {
        '': ['share/*.env','share/log/*.env'],
        'share/log': ['*.env'],
        'share': ['*.env'],
    },
    name = NAME,
    version = VERSION,
    python_requires='>=3.6',
    description = f"CLI of {NAME} a Python script",
    license = "BSD",
    url = "https://bitbucket.org/comcomai/ain-worker",
    packages=find_packages(),
    install_requires=packages,
    entry_points = {
        'console_scripts' : [f'ain = ain.ain:call']
    },
    classifiers=[
        "License :: OSI Approved :: BSD License"
    ]
)
