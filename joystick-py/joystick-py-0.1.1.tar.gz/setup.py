from setuptools import setup, find_packages

setup(
    name="joystick-py",
    version="0.1.1",
    description="Invoke plume for uploading to cloud",
    license="GPLv3",
    author="Sayan Chowdhury",
    author_email="sayan.chowdhury2012@gmail.com",
    url="https://pagure.io/joystick",
    include_package_data=True,
    packages=['joystick', 'joystick.consumers'],
    package_dir={'joystick': 'joystick'},
    package_data={'joystick': ['config/joystick.toml']},
    classifiers={
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries :: Python Modules',
    }
)
