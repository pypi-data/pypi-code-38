"""
Scripts used across the board to format all sorts outputs and strings
"""

def get_resource_type(object_name, strip=True):
    res_type = object_name.resource_type.replace(':', '')
    if strip:
        return res_type.replace('AWS', '')
    return res_type
