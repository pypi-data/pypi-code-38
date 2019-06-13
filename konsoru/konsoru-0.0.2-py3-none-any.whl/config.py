import platform

system = platform.system().lower()

# settings contains parameters for advanced usage or usage across several classes
# if misconfigured, program should raise an exception to be noticed
# so no need to use .get() when using settings
settings = {
    'shell': {
        'default_sys': 'unix',
        'allowed_commands': {
            'windows': ['echo', 'dir', 'cls', 'find', 'mkdir', 'del', 'rmdir', 'copy',
                        'rename', 'type', 'move', 'ipconfig', 'ping', 'whoami'],
            'unix': ['pwd', 'echo', 'ls', 'clear', 'cat', 'grep', 'find', 'mkdir',
                     'rm', 'rmdir', 'cp', 'mv', 'ifconfig', 'ping', 'seq', 'whoami', 'id'],
        },
        'pipe_stdout': {
            'windows': ['echo', 'find', 'type', 'whoami'],
            'unix': ['echo', 'pwd', 'ls', 'cat', 'grep', 'find', 'seq', 'whoami', 'id'],
        },
        'pipe_stderr': {
            'windows': [],
            'unix': [],
        }
    },
    'command': {
        'add_help_flag': True,
        'match_substr': False,
        'use_docstring_as_default_description': False,
    },
    'default_commands': {
        'help': ['help'],
        'exit': ['quit', 'exit'],
    },
    'rules': {
        'case_insensitive': False,
    },
}
