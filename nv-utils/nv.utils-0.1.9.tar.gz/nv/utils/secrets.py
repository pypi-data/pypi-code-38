import secrets


ALPHA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHA_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

ALPHA_SLUG = "abcdefghijklmnopqrstuvwxyz0123456789-"

ALPHANUM = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
ALPHANUM_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

ALPHANUM_SYMBOLS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)"
ALPHANUM_SYMBOLS_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)"


def generate_random_string(length: int, exclude_symbols=False, exclude_numbers=False, case_sensitive=True, slug=False,
                           allowed_chars: str = ALPHANUM_SYMBOLS) -> str:
    """
    Helper to generate random strings based on python 'secrets' lib.
    :param length: string length (positive integer)
    :param exclude_symbols: exclude main ASCII symbols "!@#$%^&*(-_=+)"
    :param exclude_numbers: exclude numbers 0-9 and symbols
    :param case_sensitive: use uppercase only letters
    :param slug: lowercase letters plus a dash bar (ulr supersafe). If True, this overrides the other settings.
    :param allowed_chars: your own set of chars in a string. Feel free to use your. This overrides the other settings.
    :return: string with a random sequence of chars, empty if length is zero.
    """

    # If exclude_numbers, exclude_symbols will be automatically set
    exclude_symbols = exclude_symbols or exclude_numbers

    if slug:
        allowed_chars = ALPHA_SLUG
    elif not exclude_symbols and not exclude_numbers:
        allowed_chars = ALPHANUM_SYMBOLS if case_sensitive else ALPHANUM_SYMBOLS_UPPER
    elif exclude_symbols and not exclude_numbers:
        allowed_chars = ALPHANUM if case_sensitive else ALPHANUM_UPPER
    elif exclude_numbers:
        allowed_chars = ALPHA if case_sensitive else ALPHANUM_UPPER

    assert length > 0, "No sense in generating a negative length string."

    if length == 0:
        return ''

    return ''.join(secrets.choice(allowed_chars) for i in range(length))


def generate_username(length, exclude_numbers=False, case_sensitive=True):
    assert length > 0, "No sense in generating a negative length string."

    if length == 0:
        return ''

    first_char = generate_random_string(1, exclude_numbers=True, case_sensitive=case_sensitive)
    rest = generate_random_string(length - 1, exclude_numbers=exclude_numbers, case_sensitive=case_sensitive)

    return f'{first_char}{rest}'
