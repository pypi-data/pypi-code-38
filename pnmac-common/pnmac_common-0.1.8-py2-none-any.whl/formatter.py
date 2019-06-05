import json
import logging

def safe_to_json(str_or_dict):
    """
    This is a simple function that will try to 
     convert an object to json safely
    """
    if type(str_or_dict) in [unicode]:
        unescaped = str_or_dict.decode('unicode-escape')
        return json.loads(str(unescaped))
    if type(str_or_dict) is str:
        return json.loads(str_or_dict)
    elif type(str_or_dict) == dict:
        return str_or_dict
    else:
        raise Exception("Unsupported type %s" % type(str_or_dict))

def safe_to_str(str_or_unicode):
    """
    Will take a str or unicode object and try to safely
     put it to string
    """
    if type(str_or_unicode) is unicode:
        return str(str_or_unicode.decode("utf-8"))
    elif type(str_or_unicode) is str:
        return str_or_unicode
    else:
        raise Exception("Unsupported type %s" % type(str_or_unicode))

def scrub_pii(d):
    """
    This is a function alias to maintain backwards compat
     Originally scrub_pii was part of formatter before moving
     to its own scrubber.py
    """
    import scrubber
    return scrubber.scrub_pii(d)