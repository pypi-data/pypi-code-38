"""This Script contains all the Exceptions used in the module"""

MESSAGE_INVALID_OS = "This module is only valid for Linux."
MESSAGE_NO_SHADOW_FILE = "Your Linux system does not use the /etc/shadow file."
MESSAGE_INVALID_PERMISSIONS_SHADOW_FILE = "Your Linux user does not have read access to the /etc/shadow file."
MESSAGE_CAT_NOT_INSTALLED = 'Your Linux system does not have the program "cat" installed.'
MESSAGE_GREP_NOT_INSTALLED = 'Your Linux system does not have the program "grep" installed.'
MESSAGE_OPENSSL_NOT_INSTALLED = 'Your Linux system does not have the program "openssl" installed.'
MESSAGE_PASSWD_NOT_INSTALLED = 'Your Linux system does not have the program "passwd" installed.'

MESSAGE_ARGUMENT_NOT_CALLABLE = "The argument is not Callable."
MESSAGE_GENERIC_INVALID_TYPE = "The argument type is not valid."
MESSAGE_INVALID_ALGORITHM_TYPE = "The algorithm can only have values from the Algorithm enum."
MESSAGE_INVALID_SALT_TYPE = "The salt must be a String."
MESSAGE_INVALID_TEXT_TYPE = "The text must be a String."
MESSAGE_INVALID_USERNAME_TYPE = "The username must be a String."
MESSAGE_INVALID_HASHED_PASSWORD_TYPE = "The hashed_password must be a String."
MESSAGE_INVALID_PASSWORD_TYPE = "The password must be a String."
MESSAGE_INVALID_SHADOW_FILE_HASH_TYPE = "The shadow_hash_file must be a String."
MESSAGE_INVALID_HASH_FORMAT = "The format for the hash is incorrect."
MESSAGE_CANT_GENERATE_HASH = "It is not possible to generate a hash based on the user's algorithm, " \
                             "if you can generate the hash try using the function validate_with_hash()"


class PrerequisiteException(Exception):
    pass


class InvalidArgumentType(Exception):
    pass


class InvalidArgumentFormat(Exception):
    pass


class ValidateUserError(Exception):
    pass
