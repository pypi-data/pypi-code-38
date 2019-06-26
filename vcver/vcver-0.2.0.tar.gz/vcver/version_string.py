def make_string_pep440_compatible(raw_str):
    """
    pep440 only allows a subset of characters in the
    version name:

    - alphanumeric
    - dots

    this will restrict the string to that set.
    """
    final_chars = []
    for r in raw_str:
        if "a" <= r <= "z" or "A" <= r <= "Z" or "0" <= r <= "9" or r == ".":
            final_chars.append(r)
    return "".join(final_chars)
