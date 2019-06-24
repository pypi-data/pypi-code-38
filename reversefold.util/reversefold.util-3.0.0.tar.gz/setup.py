# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['reversefold', 'reversefold.util']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.1,<0.5.0',
 'docopt>=0.6.2,<0.7.0',
 'fasteners>=0.15.0,<0.16.0',
 'psutil>=5.6,<6.0',
 'python-daemon==2.1.1',
 'watchdog>=0.9.0,<0.10.0']

entry_points = \
{'console_scripts': ['daemonize.py = reversefold.util.daemonize:main',
                     'log.py = reversefold.util.log:main',
                     'sort_json.py = reversefold.util.sort_json:main',
                     'stream.py = reversefold.util.stream:main',
                     'tail.py = reversefold.util.tail:main']}

setup_kwargs = {
    'name': 'reversefold.util',
    'version': '3.0.0',
    'description': 'SSH, Proc, Multiproc, tail.py, log.py, stream.py, daemonize.py, etc.',
    'long_description': "# reversefold.util\n\n[Available on pypi](https://pypi.python.org/pypi/reversefold.util)\n\nThis is a collection of various command-line scripts and libraries which have come in useful over the years I've worked with Python.\n\n\n## log.py\n\nCaptures stdout of a process and enables transformation the output (such as adding a timestamp to each line) and is compatible with external logrotate through `WatchedFileHandler`.\n\n## daemonize.py\n\nUseful for daemonizing another process which either does not daemonize itself or for which you want to capture stdout and stderr to log files. Uses `WatchedFileHandler` for output to log files to allow for external log rotation.\n\n## stream.py\n\nSimilar to `tail -f` but with some more options for type of buffering and supports streaming the entire current contents of the file before then following the tail of the file.\n\n## reversefold.util\n\n### rate_limit_gen\n\nA generator wrapper which rate-limits another generator. If the rate is exceeded, further values received within the `period` are discarded. Useful, for example, for making sure that the number of lines you display from a log file you're following don't cause your terminal to block while displaying a huge amount of output.\n\n### chunked\n\nBreaks up an iterable into equal-sized chunks.\n\n## reversefold.util.ssh\n\n### SSHHost\n\nA programmatic interface to ssh. Allows easily running a single command or a shell script or interactively sending input and displaying output. Originally written as a drop-in monkeypatch for fabric's use of paramiko.\n\n## reversefold.util.multiproc\n\n### run_subproc\n\nTakes a subprocess as input and sets up threads for handling and displaying stdout and stderr from the process. Defaults to blocking until the process is finished but also supports immediately returning and including the threads in the return value. Also defaults to capturing the stdout and stderr and returning them as lists of lines.\n\n## reversefold.util.proc\n\nProvides context managers to ensure that a process is sent a TERM or KILL signal (or both) to a process when the context block exits. Can optionally find child processes recursively and send the same signal(s) to them. Also provides functions for the same functionality.\n",
    'author': 'Justin Patrin',
    'author_email': 'papercrane@reversefold.com',
    'url': 'https://github.com/reversefold/util',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>3.4,<4',
}


setup(**setup_kwargs)
