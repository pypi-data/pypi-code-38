import re


camelcase = re.compile( r'([A-Z][a-z]+)|([a-z]+[A-Z])' )
separate_camelcase_phase_1 = re.compile( r'(.)([A-Z][a-z]+)' )
separate_camelcase_phase_2 = re.compile( r'([a-z0-9])([A-Z])' )

regex_email_validate = r'''^(?:(?:[\w`~!#$%^&*\-=+;:{}'|,?\/]+(?:(?:\.(?:"(?:\\?[\w`~!#$%^&*\-=+;:{}'|,?\/\.()<>\[\] @]|\\"|\\\\)*"|[\w`~!#$%^&*\-=+;:{}'|,?\/]+))*\.[\w`~!#$%^&*\-=+;:{}'|,?\/]+)?)|(?:"(?:\\?[\w`~!#$%^&*\-=+;:{}'|,?\/\.()<>\[\] @]|\\"|\\\\)+"))@(?:[a-zA-Z\d\-]+(?:\.[a-zA-Z\d\-]+)*|\[\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\])$'''  # noqa

email_validator = re.compile( regex_email_validate )


def test( regex, string ):
    """
    check if the string is part of the language of regex

    Arguemtens
    ----------
    regex: string or regex
    string: string

    Returns
    -------
    Bool
    """
    if isinstance( regex, str ):
        regex = re.compile( regex )
    return regex.match( string ) is not None


def is_email( email ):
    """
    check if the email is valid

    Arguments
    ---------
    email: string

    Returns
    -------
    Bool
    """
    return test( email_validator, email )


def is_camelcase( text ):
    return test( camelcase, text )
