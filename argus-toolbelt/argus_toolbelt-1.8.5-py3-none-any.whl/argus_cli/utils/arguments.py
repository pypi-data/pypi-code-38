"""Helpers for extending argument input functionality"""


def organize_parameters(include: dict, exclude: dict) -> dict:
    """Organizes parameters into argus_api format include and exclude parameters

    :param include: Parameters to include in the search
    :param exclude: Parameters to exclude in the search
    :returns: A dict that can be used on a argus_api endpoint.
    """
    include = include or {}
    exclude = exclude or {}

    parameters = {"subCriteria": []}

    for key, value in include.items():
        parameters[key] = value
    for key, value in exclude.items():
        parameters["subCriteria"].append({"exclude": True, key: value})

    return parameters


