from distutils.core import setup
setup(
    name='nesleep',
    packages = ['nesleep'],
    version='1.0',
    license='MIT',
    description = "Library and terminal command, that won't let your Mac sleep",
    author = 'Vishal Roy',
    author_email = 'hello@vishalroy.com',
    url = 'https://github.com/vishalroygeek/NeSleep',
    download_url = 'https://github.com/vishalroygeek/NeSleep/archive/1.0-beta.tar.gz',
    keywords = ['apple', 'sleep', 'lidsleep', 'command', 'terminal', 'mac', 'awake', 'avoid'],
    entry_points={
        'console_scripts': [
            'nesleep=nesleep:disableSleep'
        ]
    },
    classifiers = [ 
    'Development Status :: 4 - Beta',

    'Intended Audience :: Developers',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3',
  ],
)  