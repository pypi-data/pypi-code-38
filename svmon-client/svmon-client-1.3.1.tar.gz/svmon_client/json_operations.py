#!/usr/bin/python
# -*- coding: UTF-8 -*-


import json


def save_to_file(filename, jsondata):
    if isinstance(filename,str) == False:
        print("The filename should be a string.")
        exit(1)
    if isinstance(jsondata,dict) == False:
        print("The json data should be a dict")
        exit(1)
    with open(filename,"w") as f:
        json.dump(jsondata,f)
        return True



def load_from_file(filename):
    if isinstance(filename, str) == False:
        print("The filename should be a string.")
        exit(1)

    with open(filename, "r") as f:
        load_dict = json.load(f)
        return load_dict


if __name__ == "__main__":
    test_dict = {"site": "kit", "service_type": "13"}
    save_to_file("config.json",test_dict)
    res=load_from_file("config.json")
    print(res)
    print(type(res))

