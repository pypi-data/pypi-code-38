# TODO: Convert to using _mam.keys.Message
# nosa: E501,pylint[:Line too long]
"""Storage of custom formats."""

# file.py:1:1: E001 example error
PYCODESTYLE = '{path}:{line}:{char}: {code} {msg}'

# file.py:1: [E001] example error
PYCODESTYLE_PYLINT = '{path}:{line}: [{code}] {msg}'

# file.py:1: error: example error
MYPY = '{path}:{line}: {code}: {msg}'

# file.py:1: example error
PYFLAKES = '{path}:{line}: {msg}'

# 1:0: 'example' 1
MCCABE = "{line}:{char}: '{msg}' {code}"

# file.py:1:1: E001: example error (example-error)
PYLINT = '{path}:{line}:{char}: {code}: {msg} ({code_readable})'

# E001:001,1: module: example error
PYLINT_OLD = '{code}:{line},{char}: {extra}: {msg}'

# file.py(1): [E001foo] example error
PYLINT_VISUAL_STUDIO = '{path}({line}): [{code}{extra}] {msg}'

# file.py:1: [E001(example-error)] example error
PYLINT_PARSABLE = '{path}:{line}: [{code}({code_readable})] {msg}'

# file.py:1: example error (100% confidence)
VULTURE = '{path}:{line}: {msg} ({confidence}% confidence)'

# file.py:1:E001:HIGH:example message:HIGH:[7]
BANDIT_MAM_CUSTOM = '{path}:{line}:{code}:{severity}:{msg}:{confidence}:{range}'

# file.py:1:1: E001 error message [program]
PYLAMA = '{path}:{line}:{char}: {code} {msg} [{app}]'

# file.py:1:1: E1 ExampleError: example message
JEDI = '{file:File}:{line}:{char}: {code} {code_readable}: {msg}'

# file.py:1: example-error
PYDIATRA = '{path}:{line}: {code_readable}'

# file.py: F 1:0 example_fn - A
RADON = '{path}: {type} {line}:{char} {msg} - {code}'

# file.py - A
RADON_MI = '{path} {code}'
