#!/home/dd/anaconda3/bin/python
import os, re, json, hashlib, string
from . import lib
from . import cnf


hash_dict_filename = cnf.package_path + cnf.os_sep + 'files' + cnf.os_sep + 'hash_dict.json'

if not os.path.isfile(hash_dict_filename):
    tempDict = {}
    with open(hash_dict_filename, 'w') as f:
        json.dump(tempDict, f)


def build_hash_dict():
    
    hash_dict = {}

    for filename in omm_filenames:
        tempMix = lib.Convert.omm(filename)
        tempHash = tempMix.hash()
        hash_dict[tempHash] = tempMix.omm_oneline()
        for yotaObject in tempMix:
            tempHash = yotaObject.hash()
            hash_dict[tempHash] = yotaObject.omm

    return hash_dict


def write_hash_dict(hash_dict):

    with open('hash_dict.json','w') as f:
        json.dump(hash_dict, f)


def load_hash_dict():
    with open(hash_dict_filename, 'r') as f:
        hash_dict = json.load(f)
    return(hash_dict)


def add_to_hash_dict(mediabyte_str):
    """Add Yota/Cue/Sample/bit string to hash_dict JSON."""

    with open(hash_dict_filename, 'r') as f:
        hash_dict = json.load(f)
    
    #myObj = check_ono(mediabyte_str)
    

    def hash(mediabyte_str):
        m = hashlib.sha256()
        m.update(mediabyte_str.encode())
        temp_hash = m.hexdigest()
        for i, char in enumerate(temp_hash):
            if char in string.ascii_letters:
                calculated_hash = temp_hash[i:i+11]
                return(calculated_hash)

    no_whitespace_mediabyte_str = mediabyte_str.replace(' ', '_')
    calculated_hash = hash(no_whitespace_mediabyte_str)

    # m = hashlib.sha256()
    # m.update(mediabyte_str.encode())
    # calculated_hash = m.hexdigest()[:11]
    
    # check for Mixtape object
    mixtape_check = re.search('\.y\.', mediabyte_str)
    
    #if not mixtape_check:
    hash_dict[calculated_hash] = mediabyte_str.replace(' ','_')
    #else:
    #    hash_dict[calculated_hash] = myObj.omm_oneline()
    
    with open(hash_dict_filename, 'w') as f:
        json.dump(hash_dict, f)
    
        

def check_ono(ono_str, str=False):
    with open(hash_dict_filename, 'r') as f:
        hash_dict = json.load(f)

    keys = list(hash_dict.keys())
    m = re.search('^o\.([a-zA-Z0-9]+)', ono_str)
    o_hash = m.group(1)
    results = []
    for key in keys:
        if o_hash == key[:len(o_hash)]:
            #print(key)
            if not str:
                myObject = lib.Convert.omm(hash_dict[key])
                #return myObject
                results.append(myObject)
            else:
                #return hash_dict[key]
                results.append(hash_dict[key])
    if len(results) > 1:
        return "Multiple matches, please add characters and try again"
    elif len(results) == 1:
        return results[0]


hash_dict = load_hash_dict()