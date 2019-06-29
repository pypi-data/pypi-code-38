import setuptools

with open('README.md', 'r') as fh:
    long_desc = fh.read()


with open('LICENSE', 'r') as fh:
    license = fh.read()

setuptools.setup(
    name                          = 'Tagsnag',
    version                       = '0.10.0',
    author                        = 'Thomas Johannesmeyer',
    author_email                  = 'opensource@geeky.gent',
    description                   = 'Search files over multiple Git repos, and extract a certain version',
    long_description              = long_desc,
    long_description_content_type = 'text/markdown',
    license                       = license,
    url                           = 'https://github.com/beulenyoshi/tagsnag',
    packages                      = setuptools.find_packages(exclude = ('tests', 'docs')),
    entry_points                  = {
                                        'console_scripts': ['tagsnag=tagsnag.__main__:main'],
                                    },
    install_requires              = [

                                        ##
                                        # Interact with Git from within Python without using
                                        # the shell (too often). Careful, this seems not to be
                                        # garbage collected very well.
                                        # Fixed to 2.1.11 because I replaced a private RemoteProgress
                                        # function. See ./tagsnag/gui.py
                                        # https://github.com/gitpython-developers/GitPython/issues/871
                                        'gitpython==2.1.11',

                                        ##
                                        # Gitlab integration
                                        'python-gitlab',

                                        ##
                                        # Multiplatform GUI layer build on top of TKInter.
                                        'PySimpleGUI',

                                        ##
                                        # In comparison to the default multiprocessing module, pathos is able to
                                        # serialize almost anything in Python, including multiple argument functions
                                        # and instance methods without the hacky workaround of calling them from
                                        # the global-scope.
                                        'pathos'
                                    ],

    classifiers                   = [
                                        'Programming Language :: Python :: 3',
                                        'License :: OSI Approved :: MIT License',
                                        'Operating System :: OS Independent',
                                    ]
)
