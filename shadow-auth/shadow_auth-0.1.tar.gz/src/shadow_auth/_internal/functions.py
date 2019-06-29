"""This script contains the main authentication and hash generation functions"""

import subprocess
from shadow_auth._internal.classes import ShadowHash
from shadow_auth._internal.enums import Algorithm
from shadow_auth._internal.validations import (
    validate_system_requirements_first
)

from shadow_auth._internal.exceptions import (
    # Exceptions
    InvalidArgumentType,
    ValidateUserError,

    # Exception Messages
    MESSAGE_INVALID_ALGORITHM_TYPE,
    MESSAGE_INVALID_SALT_TYPE,
    MESSAGE_INVALID_TEXT_TYPE,
    MESSAGE_INVALID_USERNAME_TYPE,
    MESSAGE_INVALID_HASHED_PASSWORD_TYPE,
    MESSAGE_INVALID_PASSWORD_TYPE,
    MESSAGE_CANT_GENERATE_HASH
)


def _generate_openssl_hash(algorithm: Algorithm, salt: str, text: str) -> str:
    """
    Internal function that generates a Hash using the openssl program.

    :param algorithm: A valid hashing algorithm to be used
    :param salt: The salt added when generating the hash
    :param text: The text to be hashed
    :return: A hashed string
    :raises InvalidArgumentType:
    """
    if not isinstance(algorithm, Algorithm):
        raise InvalidArgumentType(MESSAGE_INVALID_ALGORITHM_TYPE)
    if not isinstance(salt, str):
        raise InvalidArgumentType(MESSAGE_INVALID_SALT_TYPE)
    if not isinstance(text, str):
        raise InvalidArgumentType(MESSAGE_INVALID_TEXT_TYPE)

    result = subprocess.check_output(
        "echo {text} | openssl passwd -{algorithm} -salt {salt} -stdin".format(
            text=text,
            algorithm=algorithm.value,
            salt=salt
        ),
        shell=True
    ).decode("utf-8")[:-1]

    return result


def _generate_random_openssl_hash() -> str:
    """Internal function that generates a random Hash using the openssl program."""
    from random import choice
    from string import ascii_letters

    random_string: str = lambda size: ''.join(choice(ascii_letters) for x in range(size))
    algorithm: Algorithm = choice([Algorithm.MD5, Algorithm.SHA_256, Algorithm.SHA_512])
    salt: str = random_string(8)
    text: str = random_string(choice([5,6,7,8,9,10]))

    result = _generate_openssl_hash(algorithm=algorithm, salt=salt, text=text)
    return result


def _generate_fake_user_hash(username: str) -> str:
    """Internal function that generates a fake reproducible Hash using the openssl program."""

    hashed_username = str(abs(hash(username+"abcd")))

    i = 0
    while len(hashed_username) < 8:
        hashed_username = hashed_username + hashed_username[i]
        i += 1

    salt_text = ""
    for letter_index in range(8):
        char_num =int(hashed_username[letter_index])
        if char_num %2 == 0:
            salt_text = salt_text + chr(65 + char_num)
        else:
            salt_text = salt_text + chr(97 + char_num)

    return _generate_openssl_hash(algorithm=Algorithm.SHA_512, salt=salt_text, text=salt_text)


def _get_user_password_hash_from_shadow_file(username: str) -> str:
    """
    Internal function that retrieves the password hash from a Linux user.
    If the user does not exist a fake result is returned as a safety measure.

    :param username: A valid hashing algorithm to be used
    :return: A the hashed password string
    :raises InvalidArgumentType:
    """
    if not isinstance(username, str):
        raise InvalidArgumentType(MESSAGE_INVALID_USERNAME_TYPE)

    try:
        result = subprocess.check_output(
            "cat /etc/shadow | grep {user}".format(user=username),
            shell=True
        ).decode("utf-8").split(":")[1]
        return result
    except subprocess.CalledProcessError:
        return _generate_random_openssl_hash()


@validate_system_requirements_first
def generate_openssl_hash(algorithm: Algorithm, salt: str, text: str) -> str:
    """
    Generates a Hash using the openssl program.

    :param algorithm: A valid hashing algorithm to be used
    :param salt: The salt added when generating the hash
    :param text: The text to be hashed
    :return: A hashed string
    :raises PrerequisiteException, InvalidArgumentType:
    """
    if not isinstance(algorithm, Algorithm):
        raise InvalidArgumentType(MESSAGE_INVALID_ALGORITHM_TYPE)
    if not isinstance(salt, str):
        raise InvalidArgumentType(MESSAGE_INVALID_SALT_TYPE)
    if not isinstance(text, str):
        raise InvalidArgumentType(MESSAGE_INVALID_TEXT_TYPE)
    result = _generate_openssl_hash(algorithm=algorithm, salt=salt, text=text)
    return result


@validate_system_requirements_first
def validate_with_hash(username: str, hashed_password: str) -> bool:
    """
    Validates the given credentials for a user in the system using a hashed password.
    A random hash is used to compare the provided hash as a safety measure if the user does not exist,
    has a blank password, or the account is disabled.

    :param username: The user to be validated in the system
    :param hashed_password: The password hash to be used to compare the credentials
    :return: true if credentials are valid, false if they are not.
    :raises PrerequisiteException, InvalidArgumentType, InvalidArgumentFormat:
    """
    if not isinstance(username, str):
        raise InvalidArgumentType(MESSAGE_INVALID_USERNAME_TYPE)

    if not isinstance(hashed_password, str):
        raise InvalidArgumentType(MESSAGE_INVALID_HASHED_PASSWORD_TYPE)

    if len(hashed_password.split("$")) != 4:
        return False

    user_hash = _get_user_password_hash_from_shadow_file(username)
    if (user_hash == "") or ("!" in user_hash) or ("*" in user_hash) or ("$" not in user_hash):
        user_hash = _generate_random_openssl_hash()
    shadow_object = ShadowHash(hashed_password)
    return shadow_object.equals(user_hash)


@validate_system_requirements_first
def validate_with_password(username: str, password: str) -> bool:
    """
    Validates the given credentials for a user in the system using a string password.
    A random hash is used to compare the provided password as a safety measure if the user does not exist,
    has a blank password, or the account is disabled.

    :param username: The user to be validated in the system
    :param password: The password to be used to compare the credentials
    :return: true if credentials are valid, false if they are not
    :raises PrerequisiteException, InvalidArgumentType, InvalidArgumentFormat, ValidateUserError:
    """
    if not isinstance(username, str):
        raise InvalidArgumentType(MESSAGE_INVALID_USERNAME_TYPE)
    if not isinstance(password, str):
        raise InvalidArgumentType(MESSAGE_INVALID_PASSWORD_TYPE)

    user_hash = _get_user_password_hash_from_shadow_file(username)
    if (user_hash == "") or ("!" in user_hash) or ("*" in user_hash) or ("$" not in user_hash):
        user_hash = _generate_random_openssl_hash()
    shadow_object = ShadowHash(user_hash)
    if shadow_object.algorithm not in [enum.value for enum in Algorithm]:
        raise ValidateUserError(MESSAGE_CANT_GENERATE_HASH)
    return shadow_object.equals(_generate_openssl_hash(
                                    algorithm=Algorithm(shadow_object.algorithm),
                                    salt=shadow_object.salt,
                                    text=password)
                                )


@validate_system_requirements_first
def get_password_info(username: str) -> dict:
    """
    Returns the type of algorithm and salt of a user.
    A fake result is returned as a safety measure if the user does not exist,
    has a blank password, or the account is disabled.

    :param username: The user in the system
    :return: {"algorithm": "xxxx", "salt": "xxxx"}
    :raises PrerequisiteException, InvalidArgumentType:
    """
    if not isinstance(username, str):
        raise InvalidArgumentType(MESSAGE_INVALID_USERNAME_TYPE)

    try:
        user_hash = subprocess.check_output(
            "cat /etc/shadow | grep {user}".format(user=username),
            shell=True
        ).decode("utf-8").split(":")[1]

    except subprocess.CalledProcessError:
        user_hash = _generate_fake_user_hash(username)

    if (user_hash == "") or ("!" in user_hash) or ("*" in user_hash) or ("$" not in user_hash):
        user_hash = _generate_fake_user_hash(username)

    split_hash = user_hash.split("$")

    return {"algorithm": split_hash[1], "salt": split_hash[2]}
