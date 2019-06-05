import json
import logging

def safe_to_json(str_or_dict):
    """
    This is a simple function that will try to 
     convert an object to json safely
    """
    if type(str_or_dict) in [unicode, str]:
        return json.loads(str_or_dict)
    elif type(str_or_dict) == dict:
        return str_or_dict
    else:
        raise Exception("Unsupported type %s" % type(str_or_dict))

def scrub_pii(d):
    """
    This is a function alias to maintain backwards compat
     Originally scrub_pii was part of formatter before moving
     to its own scrubber.py
    """
    import scrubber
    return scrubber.scrub_pii(d)