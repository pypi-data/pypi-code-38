import hashlib
import warnings

import requests
import six

import pyhibp

PWNED_PASSWORDS_API_BASE_URI = "https://api.pwnedpasswords.com/"
PWNED_PASSWORDS_API_ENDPOINT_RANGE_SEARCH = "range/"

RESPONSE_ENCODING = "utf-8-sig"


def is_password_breached(password=None, sha1_hash=None, first_5_hash_chars=None):
    """
    Execute a search for a password via the k-anonymity model, checking for hashes which match a specified
    prefix instead of supplying the full hash to the Pwned Passwords API.

    Uses the first five characters of a SHA-1 hash to provide a list of hash suffixes along with the
    number of times that hash appears in the data set. In doing so, the API is not provided the information
    required to reconstruct the password (e.g., by brute-forcing the hash).

    Either ```password`` or ``sha1_hash`` must be specified. Only one parameter should be provided.

    The precedence of parameters is as follows:
    1) password - Used to compute the SHA-1 hash of the password.
    2) sha1_hash - The hash prefix (hash[0:5]) is passed to the HIBP API, and this function will check the returned list of
    hash suffixes to determine if a breached password was in the HIBP database.

    Note: Suffix searches, that is, to retrieve a list of hash suffixes by supplying a hash prefix, have moved to
    `suffix_search()` as of this release (v3.1.0). A compatability shim has been left for this release, but will be removed on the
    next major version release.

    :param password: The password to check. Will be converted to a SHA-1 string. `str` type.
    :param sha1_hash: A full SHA-1 hash. `str` type.
    :return: An Integer representing the number of times the password is in the data set; if not found,
    Integer zero (0) is returned.
    :rtype: int
    """
    # Parameter validation section
    if not any([password, first_5_hash_chars, sha1_hash]):
        raise AttributeError("One of password, sha1_hash, or first_5_hash_chars must be provided.")
    elif password is not None and not isinstance(password, six.string_types):
        raise AttributeError("password must be a string type.")
    elif sha1_hash is not None and not isinstance(sha1_hash, six.string_types):
        raise AttributeError("sha1_hash must be a string type.")
    elif first_5_hash_chars is not None and not isinstance(first_5_hash_chars, six.string_types):
        raise AttributeError("first_5_hash_chars must be a string type.")
    if first_5_hash_chars and len(first_5_hash_chars) != 5:
        raise AttributeError("first_5_hash_chars must be of length 5.")

    if password:
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest()
    if sha1_hash:
        # The HIBP API stores the SHA-1 hashes in uppercase, so ensure we have it as uppercase here
        sha1_hash = sha1_hash.upper()
        first_5_hash_chars = sha1_hash[0:5]

    suffix_list = suffix_search(hash_prefix=first_5_hash_chars)

    if not sha1_hash:
        # TODO: v4.0.0: Remove this codepath (first_5_hash_chars)
        warnings.warn("""
            Hash suffix searching is being moved to its own discrete function, `suffix_search()`. Call `suffix_search(hash_prefix=prefix)`
            instead. Hash prefixes will not return from is_password_breached() in a future release.
        """)
        # Return the list of hash suffixes.
        return suffix_list
    else:
        # Since the full SHA-1 hash was provided, check to see if it was in the resultant hash suffixes returned.
        for hash_suffix in suffix_list:
            if sha1_hash[5:] in hash_suffix:
                # We found the full hash, so return
                return int(hash_suffix.split(':')[1])

        # If we get here, there was no match to the supplied SHA-1 hash; return zero.
        return 0


def suffix_search(hash_prefix=None):
    """
    Returns a list of SHA-1 hash suffixes, consisting of the SHA-1 hash characters after position five,
    and the number of times that password hash was found in the HIBP database, colon separated.

    Leveraging the k-Anonymity model, a list of hashes matching a specified SHA-1 prefix are returned.
    From this list, the calling application may determine if a given password was breached by comparing
    the remainder of the SHA-1 hash against the returned results. As an example, for the hash prefix of
    '42042', the hash suffixes would be:

    ```
    005F4A4B9265A2BABE10B1A9AB9409EA3F0:1
    00D6F0319225107BD5736B72717BD381660:8
    01355DCE0B54F0E8DBBBA8F7B9A9872858A:15
    0163E1C872A64A62625F5EB2F3807B7F90B:2
    020DDE278E6A9C05B356C929F254CE6AED5:1
    021EFB4FAE348050D9EDCD10F8B6A87C957:4
    ...
    ```

    If the `prefix` and `suffix` form a complete SHA-1 hash for the password being compared, then it
    indicates the password has been found in the HIBP database.

    :param hash_prefix: The first five characters of a SHA-1 hash. `str` type.
    :return: A list of hash suffixes.
    :rtype: list
    """
    if not hash_prefix or not isinstance(hash_prefix, six.string_types):
        raise AttributeError("hash_prefix must be a supplied, and be a string-type.")
    if hash_prefix and len(hash_prefix) != 5:
        raise AttributeError("hash_prefix must be of length 5.")

    uri = PWNED_PASSWORDS_API_BASE_URI + PWNED_PASSWORDS_API_ENDPOINT_RANGE_SEARCH + hash_prefix

    resp = requests.get(url=uri, headers=pyhibp.pyHIBP_HEADERS)
    if resp.status_code != 200:
        # The HTTP Status should always be 200 for this request
        raise RuntimeError("Response from the endpoint was not HTTP200; this should not happen. Code was: {0}".format(resp.status_code))
    # The server response will have a BOM if we don't do this.
    resp.encoding = RESPONSE_ENCODING

    return resp.text.split()
