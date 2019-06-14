"""
main.py
Main file for package containing basic functions.   
This file is part of the userutils package https://github.com/Scoder12/userutils

Copyright 2018 Scoder12

Licensed under the MIT License.  

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the
following conditions: 

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import json


def yesNo(msg, loop=True, incorrmsg="Please answer yes or no. "):
    """Asks a user msg where the reponse shoud be yes or no.

    Args:
        msg (str): message to be asked of user
        loop (bool): Whether to loop on invalid input or not
        incorrmsg (str) [optional]: message to be printed if the user enters an invalid
        input.
    Returns:
        True if the user answers yes
        False if the user answers no
    """
    first = True
    while loop or first:
        first = False
        i = input(msg)
        if i[0].lower() == 'y':
            return True
        elif i[0].lower() == 'n':
            return False
        print(incorrmsg)


inps = []


def getJSON(msg, loop=True, smart=True, 
printerror=True, invalidjsonmsg="Please input some valid JSON!", enforcedtype=None, invalidtypemsg="Please enter the requested type. "):
    """Gets JSON from the user. 

    Args:
        msg (str): Message to be shown for the prompt
        loop (bool): Loop if invalid input recieved
        smart (bool): Detect common errors and prompt user to fix them. Default True
        invalidmsg (str): Message to be shown on invalid input
        enforcedtype (any): If not None, then it will fail if it is a different type. Default: None
    Returns:
        The JSON object provided. 
    """
    global inps
    first = True
    while loop or first:
        first = False
        if len(inps) > 0:
            i = inps[0]
            inps.pop(0)
        else:
            i = input(msg)
        try:
            j = json.loads(i)
        except Exception as e:
            if hasattr(e, 'message'):
                m = str(e.message)
            else:
                m = str(e)
            if printerror:
                print(m)
            if m.startswith('Expecting property name enclosed in double quotes:'):
                if yesNo('Non-double quotes detected. JSON must have double '
                         'quotes to be parsed. Parse the JSON with all single'
                         'quotes converted to double and escape double quotes? '
                         ):
                    i = i.replace('"', '\\"')
                    i = i.replace("'", '"')
                    inps.append(i)
                else:
                    print(invalidjsonmsg)
                continue
            print(invalidjsonmsg)
        else:
            if enforcedtype is not None:
                if type(j) != enforcedtype:
                    print(invalidtypemsg)
                    continue
            inps = []  # clear any inputs so as to not accidentally load them next run
            return j
        continue
