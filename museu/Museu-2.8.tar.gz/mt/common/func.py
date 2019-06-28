#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-04-26 09:15:03
# @Author  : Blackstone
# @to      :

def dot_name_to_object(name,is_greedy=False):
    """Resolve a dotted name to a global object exclude packagename(a.b or .a.b)

         default(is_greedy=False) return "undefined" if can't found.

         else(is_greedy=True)  try best match : module._xda  => moudle if _xda can not import


    """

    found="undefined"

    try:

        name = name.split('.')
        used = name.pop(0)
        #print(name)
        #print(used)
        found = __import__(used)
       # print(found)
        for n in name:
        	
            used = used + '.' + n

            #print("used=>",used)
            try:
                #print("found=>",found)
               # print("n=>",n)
                found = getattr(found, n)
                #print("found=>",found)
            except AttributeError:
                try:
                    __import__(used)
                    found = getattr(found, n)
                except ValueError as e:
                    if not is_greedy:
                        found="undefined"
    except:
        if not is_greedy:
            found="undefined"    

    finally:
        return found