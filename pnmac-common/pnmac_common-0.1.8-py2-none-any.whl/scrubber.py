import logging
import ast

#logging.getLogger().setLevel(logging.WARN)

def scrub_pii(d):
    import formatter
    """
    This function will attempt to read scrub PII out of it 
     base on the keys it has

    Parameters
    -----
    d: dict
     This is the dict (or a stringy dict) you hope to scrub

    """
    

    if type(d) != dict:
        try:
            if d is unicode:
                d = formatter.safe_to_str(d)
            scrub_object = ast.literal_eval(d)
            #scrub_pii(scrub_object) #Not needed? We don't alter the underlying object
        except ValueError:
            logging.error("PII scrubber only works on dict-y objects, your object was %s" % type(d))
            return None
    else:
        scrub_object = d.copy() 

    for key, value in scrub_object.items():
        #print("Key: %s" % key)
        #print("Value type: %s" % type(value))
        if type(value) is unicode:
            value = formatter.safe_to_str(value)
        if type(value) in [str]:
            try:
                value = ast.literal_eval(value)
            except ValueError:
                try:
                    value = formatter.safe_to_json(value)
                except ValueError:
                    pass
            except SyntaxError:
                pass
        #print("After processing type(value): %s" % type(value))
        if type(value) in [str,int,unicode]:
            scrub_object[key] = _scrub_key(key, value)
        elif isinstance(value,dict):
            scrub_object[key] = scrub_pii(value)
        elif isinstance(value,list):
            scrubbed = []
            for item in value:
                scrubbed.append(scrub_pii(item))
            scrub_object[key] = scrubbed

    return scrub_object

def _scrub_key(key, value):

    #Return zero len keys
    try:
        if len(value) == 0:
            return value
    except TypeError:
        pass

    #print("Trying to scrub %s" % key)
    standard_key = key.lower()\
        .strip()\
        .replace("_","")\
        .replace(" ","")\
        .replace("-","")

    for item in _get_scrub_pii_field_names():
        if item in standard_key:
            logging.debug("Scrubbing %s" % standard_key)
            return str(value)[0]+"****"+str(value)[-1]
    return value

def _get_scrub_pii_field_names():
    return [
        #Name
        "lastname","lname","fullname","mname","middlename"
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
        ,"personid","pid","uid"
        #Passwords
        ,"password","pw"
        #Financial Info
        ,"balance","bal"
        ,"salary","income"
        ,"paycheck"
        #Identifing Docs
        ,"passport"
        ,"license"
        ,"ident"
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
                "ok_cupid": "m****h"
                }
            ],
        "listystrings": [{'ssn': '1****2'},{'ok_cupid':False},{'address': '1****e'}]
        }
    
    assert scrub_pii(my_json) == expected_json