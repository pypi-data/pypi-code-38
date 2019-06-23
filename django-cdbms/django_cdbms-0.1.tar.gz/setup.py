from distutils.core import setup

setup(
    name='django_cdbms',  # How you named your package folder (MyLib)
    packages=['django_cdbms'],  # Chose the same as "name"
    version='0.1',  # Start with a small number and increase it with every change you make
    license='MIT',
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Library for using multiple databases of different models.',
    # Give a short description about your library
    author='Timur Timerkhanov',  # Type in your name
    author_email='timurgrunge@gmail.com',  # Type in your E-Mail
    url='https://github.com/TTimerkhanov/django_cdbms/',
    # Provide either the link to your github or to your website
    download_url='https://github.com/TTimerkhanov/django_cdbms/archive/v_01.tar.gz',
    # I explain this later on
    keywords=[],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'Django',
        'djongo',
        'neomodel',
        'psycopg2',
        'future',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',
        # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.6',
    ],
)
