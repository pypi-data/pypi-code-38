from .raise_ import raise_

ascDescSet = {"asc", "desc"}


def sanitizeAscDesc(ascOrDesc):
    sanitized = ascOrDesc.lower()
    if sanitized not in ascDescSet:
        raise_(
            ValueError,
            f"""
            ascOrDesc must be either 'asc' or 'desc' (case insensitive)
            value given: {ascOrDesc}
            """,
        )

    return sanitized
