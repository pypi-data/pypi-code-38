from ..exceptions import InvalidParameterError
from re import search as s


def check_postcode_is_valid_uk_format(post_code):
    """ Check a post_code is of valid formatting. This function will not
    verify whether a post_code actually exists, that responsibility lies
    with the client. This function does not take BFPO post_code. If the
    post code is not valid, throw an error.

    :Args:
     post_code - A post_code provided by the post.customer()
        function
    """
    r = s(
        '^([A-Za-z][A-Ha-hJ-Yj-y]?[0-9][A-Za-z0-9]? ?[0-9][A-Za-z]{2}|[Gg][Ii]'
        '[Rr] ?0[Aa]{2})$', post_code
    )
    if not r:
        raise InvalidParameterError(
            '%s is not formatted as a UK post code. Please check the post code'
            ' and re-submit.' % post_code
        )
    else:
        pass


def check_email_address_format(email_address):
    """ Check an email_address is of valid formatting. This function
    will not verify whether a email_address actually exists, instead
    it checks that an email could exist. The responsibility of checking
    that an email actually exists lies with the client. If the email
    formatting is invalid, throw an error.

    :Args:
     email_address - An email_address provided by the post.customer()
        function
    """
    r = s(
        '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', email_address
    )
    if not r:
        raise InvalidParameterError(
            '%s is not a valid email address. Please check the email address'
            ' and re-submit.' % email_address
        )
    else:
        pass


def check_bank_details_format(account_number, sort_code, account_name):
    """ Check an account_number, sort_code and account_name are all of
    valid formatting. This function does not verify whether or not a
    bank account exists, or whether it could exist. It simply checks the
    length of the three arguments. The responsibility of verifying the
    legitimacy of the account details lies with the client. If any of
    the three values are not the correct formatting, throw an error.

    :Args:
     account_number - An account_number provided by the post.customer()
        function
     sort_code - A sort_code provided by the post.customer()
        function
     account_name - An account_name provided by the post.customer()
        function
    """
    num_r = s(
        '^[0-9]{8}$', account_number
    )
    sort_r = s(
        '^[0-9]{6}$', sort_code
    )
    name_r = s(
        '^[A-Z0-9\-\/& ]{3,18}$', account_name.upper()
    )
    if not num_r:
        raise InvalidParameterError(
            '%s is not formatted as a UK bank account number. UK bank'
            ' account numbers are 8 digits long. Please check the bank'
            ' account number and re-submit.' % account_number
        )
    elif not sort_r:
        raise InvalidParameterError(
            '%s is not formatted as a UK sort code. UK sort codes are 6 digits'
            ' long. Make sure to not include any hyphens. Please check the'
            ' sort code and re-submit.' % sort_code
        )
    elif not name_r:
        raise InvalidParameterError(
            '%s is not formatted as an account holder name. Account holder'
            ' names must be between 3 and 18 characters, contain only capital'
            ' letters (A-7), ampersands (&), hyphens (-), forward'
            ' slashes (/), and spaces ( ).' % account_name
        )
    else:
        pass
