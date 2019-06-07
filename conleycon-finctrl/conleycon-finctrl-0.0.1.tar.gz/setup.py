import setuptools

setuptools.setup(
    name='conleycon-finctrl',
    version='0.0.1',
    author='Christopher Covington',
    description='Tools for parsing financial transaction emails',
    url='https://gitlab.com/conleycon/finctrl',
    packages=['conleycon.finctrl'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved',
        # Not yet on pypi.org
        #'License :: OSI Approved :: Zero-Clause BSD (0BSD)',
        'Operating System :: OS Independent',
        'Topic :: Communications :: Email',
    ],
    license='0BSD',
    scripts=[
        'conleycon/finctrl/email2caldav.py',
        'conleycon/finctrl/json2caldav.py',
    ],
    include_package_data=True,
)
