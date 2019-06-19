# Copyright (C) 2015-2017  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information


PRIMARY_ALGO = 'sha1_git'


def parse_author(name_email):
    """Parse an author line"""

    if name_email is None:
        return None

    try:
        open_bracket = name_email.index(b'<')
    except ValueError:
        name = email = None
    else:
        raw_name = name_email[:open_bracket]
        raw_email = name_email[open_bracket+1:]

        if not raw_name:
            name = None
        elif raw_name.endswith(b' '):
            name = raw_name[:-1]
        else:
            name = raw_name

        try:
            close_bracket = raw_email.index(b'>')
        except ValueError:
            email = None
        else:
            email = raw_email[:close_bracket]

    return {
        'name': name,
        'email': email,
        'fullname': name_email,
    }
