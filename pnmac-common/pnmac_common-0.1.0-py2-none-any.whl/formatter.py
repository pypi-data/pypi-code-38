import json
import logging
import parser
import ast

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
    This function will attempt to read scrub PII out of it 
     base on the keys it has


    """
    if type(d) != dict:
        try:
            scrub_object = ast.literal_eval(d)
            scrub_pii(scrub_object)
        except ValueError:
            logging.error("PII scrubber only works on dict types, your object was %s" % type(scrub_object))
            return scrub_object
    else:
        scrub_object = d.copy() 

    for key, value in scrub_object.items():
        if type(value) is str:
            try:
                value = ast.literal_eval(value)
            except ValueError, TypeError:
                pass
            except SyntaxError:
                pass
        if type(value) in [str,int]:
            scrub_object[key] = _scrub_key(key, value)
        elif isinstance(value,dict):
            scrub_object[key] = scrub_pii(value)
        elif isinstance(value,list):
            scrubbed = []
            for item in value:
                print(item)
                scrubbed.append(scrub_pii(item))
            scrub_object[key] = scrubbed

    return scrub_object

def _scrub_key(key, value):
    standard_key = key.lower()\
        .strip()\
        .replace("_","")\
        .replace(" ","")\
        .replace("-","")

    for item in _get_scrub_pii_field_names():
        if item in standard_key:
            return str(value)[0]+"****"+str(value)[-1]
    return value

def _get_scrub_pii_field_names():
    return [
        #Name
        "lastname","lname","fullname"
        #Address
        ,"zip","postal","addr"
        #Social
        ,"social","ssn"
        #Loan
        ,"loann" #loannumber or loanno
        #Contact
        ,"email","phone","mobile","cell"
        #DOB
        ,"birth","dob"
        #Username
        ,"username","login","userid","account"
        #Passport
        ,"passport"
    ]

def test_scrub_pii():
    my_json = {
        "first_name": "john",
        "last_name": "Rhoads",
        "lastName": "Rhoads",
        "lname": "Rhoads",
        "zipcode": {
            "sub": 12345,
            "zippy": "12293-1232"
            },
        "anotherone": "{'my_value': True, 'ssn': '200-66-5940'}",
        "listy": [
            {
                "ssn": 123213222
                },
            {
                "ok_cupid": "match"
                }
            ],
        "listystrings": ["{'ssn': 1232112}","{'ok_cupid':False}","{'address': '14 marker drive'}"]
        }
    
    expected_json = { "first_name": "john",
        "last_name": "R****s",
        "lastName": "R****s",
        "lname": "R****s",
        "zipcode": {
            "sub": 12345,
            "zippy": "1****2"
            },
        "anotherone": {'my_value': True, 'ssn': '2****0'},
        "listy": [
            {
                "ssn": "1****2"
                },
            {
                "ok_cupid": "match"
                }
            ],
        "listystrings": [{'ssn': '1****2'},{'ok_cupid':False},{'address': '1****e'}]
        }
    
    assert scrub_pii(my_json) == expected_json