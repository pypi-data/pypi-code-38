from bwsi_grader.errors import DeveloperError


def print_passed(hash_str: str):
    """
    Prints the ALL TESTS PASSED message with the included hash.

    The characters 'bw' are prepended to the hash.

    Parameters
    ----------
    hash_str : str
        A 56-character hash to be submitted by students

    Raises
    ------
    DeveloperError
        `hash_str` must be 56 characters.
    """
    if len(hash_str) != 56:
        raise DeveloperError(f"`hash_str` must contain 56 characters. "
                             f"Got {len(hash_str)} characters")
    msg = f"""
============================== ALL TESTS PASSED! ===============================
Your submission code: bw{hash_str}
================================================================================
"""
    print(msg)
