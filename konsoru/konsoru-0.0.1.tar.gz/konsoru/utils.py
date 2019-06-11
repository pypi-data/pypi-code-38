from . import config


if config.system != 'windows':
    import termios, copy, readline

    class TerminalMode:
        NORMAL = 'normal'
        NONECHO = 'nonecho'
        # NONCANONICAL = 'noncanonical'

        def __init__(self, mode):
            self._saved_attr = None
            self._mode = mode
            self._fd = None

        def __enter__(self):
            if self._mode == TerminalMode.NORMAL:
                return
            elif self._mode == TerminalMode.NONECHO:
                self._fd = 0
                attr = termios.tcgetattr(self._fd)
                self._saved_attr = copy.deepcopy(attr)
                attr[3] &= ~termios.ECHO
                termios.tcsetattr(self._fd, termios.TCSANOW, attr)

        def __exit__(self, type, value, traceback):
            # restore previous terminal settings
            if self._saved_attr is not None:
                termios.tcsetattr(0, termios.TCSANOW, self._saved_attr)


    def enter_password(prompt='Password: ', hash_method=None):
        import hashlib
        hashmap = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha224': hashlib.sha224,
            'sha256': hashlib.sha256,
            'sha384': hashlib.sha384,
        }
        with TerminalMode(mode=TerminalMode.NONECHO):
            user_input = ask_user_input(prompt)
            if isinstance(hash_method, str):
                if hash_method not in hashmap:
                    raise ValueError('Unsupported hash method: %s' % hash_method)
                hash_method = hashmap[hash_method]
                hashobj = hash_method(user_input.encode())
                ret = hashobj.hexdigest()
            elif hash_method is None:
                ret = user_input
            else:
                raise ValueError("Parameter 'hash_method' must be a NoneType or str!")
            del user_input
            print()
            return ret


def ask_user_input(prompt=''):
    """
    Ask user input without being put into readline history.

    Parameters
    ----------
    prompt : str
        Prompt passed to input() function.
    """

    if config.system == 'windows':
        user_input = input(prompt)
    else:
        try:
            readline.set_auto_history(False)
            user_input = input(prompt)
        finally:
            readline.set_auto_history(True)
    return user_input


def ask_yes_or_no(prompt='Are you sure?'):
    """
    Ask yes or no until user explicitly answers and return True for yes, and
    False for no. User must answer with exactly matching yes or no, or a
    single character y or n. Answer is case insensitive.

    Parameters
    ----------
    prompt : str
        Message given to user. A "(y/n)" string is automatically appended to
        the end.

    Returns
    -------
    ans : bool
        True for yes, False for no.
    """
    prompt += ' (y/n) '
    while True:
        user_input = ask_user_input(prompt)
        user_input = user_input.lower()
        if user_input == 'yes' or user_input == 'y':
            return True
        elif user_input == 'no' or user_input == 'n':
            return False
