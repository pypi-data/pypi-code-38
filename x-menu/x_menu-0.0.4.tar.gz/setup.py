
from setuptools import setup, find_packages


setup(name='x_menu',
    version='0.0.4',
    description='api for console ui',
    url='https://github.com/Qingluan/console-ui.git',
    author='auth',
    author_email='darkhackdevil@gmail.com',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=[''],
    entry_points={
        'console_scripts': ['']
    },

)
