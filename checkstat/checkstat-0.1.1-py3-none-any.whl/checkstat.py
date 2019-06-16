import requests


def is_up(webpage):
    """Return True if 200 code was received, else return False."""
    try:
        req = requests.get(webpage)

    # On connection error, return False.
    except requests.exceptions.ConnectionError:
        return False
    # Connection was successful, return True on 200 code, else return False.
    else:
        if req.status_code == 200:
            return True
        return False
