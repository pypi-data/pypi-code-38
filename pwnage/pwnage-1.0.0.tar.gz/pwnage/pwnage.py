#!/usr/bin/env python

#########################################################################################
# NAME: pwnage.py
# 
# Website: https://github.com/zloether/pwnage
#
# Description: Checks passwords against the Have I Been Pwned database to see if 
#               the password has been compromised.
# https://haveibeenpwned.com/
#########################################################################################


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import requests
from hashlib import sha1
from io import StringIO
import argparse
import urllib
import getpass
import passgenerator



# -----------------------------------------------------------------------------
# Call the API
# -----------------------------------------------------------------------------
def call_hibp_api(url, debug=False, params=None):
    headers = {
        'api-version': '2',
        'User-Agent': 'pwnage.py'
    }

    if debug:
        print('URL: ' + str(url))
        print('Headers: ' + str(headers))
        print('Params: ' + str(params))
        print('Attempting to connect to API')

    # make the request
    r = requests.get(url, headers=headers, params=params)

    # return response
    return r



# -----------------------------------------------------------------------------
# Look for pwned accounts
# -----------------------------------------------------------------------------
def account_pwnage(input_account, debug=False, truncate_reponse=True):
    # url encode the account
    url_account = urllib.parse.quote(input_account)

    # set parameters for API call
    if truncate_reponse:
        params = {'truncateResponse': 'true', 'includeUnverified': 'true'}
    else:
        #params = None
        params = {'includeUnverified': 'true'}

    # build URL
    url = 'https://haveibeenpwned.com/api/v2/breachedaccount/' + url_account

    # call the API
    response = call_hibp_api(url, debug=debug, params=params)
    
    # parse reponse
    parse_account_response(response, input_account, debug, truncate_reponse)



# -----------------------------------------------------------------------------
# Parse account response
# -----------------------------------------------------------------------------
def parse_account_response(response, input_account, debug=False, truncate_reponse=False):
    if response.status_code == 404: # account not pwned!
        print(str(input_account) + ' has not been pwned!')

    elif response.status_code == 200: # account pwned!
        j = response.json() # get the json
        
        # print the bad news
        print(str(input_account + ' has been pwned in these breaches:'))

        if not truncate_reponse: # truncated response
            for breach in j: # iterate through the breaches
                
                # pull out the details we want to print
                name = breach['Name']
                date = breach['BreachDate']
                classes = breach['DataClasses']
                verified = breach['IsVerified']
                if verified:
                    ver_status = 'Verified'
                else:
                    ver_status = 'Unverified'
                
                # format classes info for output
                class_string = "" # string for holding classes info
                i = 0 # counter
                while i < len(classes)-1: # iterate through all but last entry in list
                    class_string = class_string + classes[i] + ', '
                    i += 1 # iterate counter
                class_string = class_string + classes[len(classes)-1] # get the last entry

                # print details
                print(str(ver_status) + ': ' + str(name) + ' on ' + str(date) + '. Details leaked: ' + str(class_string))
        
        else: # truncated response
            for i in j: # loop through json
                print(i['Name']) # print details

    else: # response code isn't 200 or 404
        print('Error reaching API')
        if debug:
            print('Response code: ' + str(response.status_code))
        exit()



# -----------------------------------------------------------------------------
# Look for pwned passwords
# -----------------------------------------------------------------------------
def password_pwnage(input_password, debug=False, print_output=True, return_output=False):
    hashed_pass = sha1(input_password.encode()).hexdigest() # get hash of password
    hash_prefix = hashed_pass[:5] # get first 5 characters of hashed password
    hash_suffix = hashed_pass[5:] # get characters except first 5 from hashed password
    if debug:
        print("Input password: " + str(input_password))
        print("Hashed passwword: " + str(hashed_pass))
        print("Hashed password prefix: " + str(hash_prefix))
        print("Hashed password suffix: " + str(hash_suffix))
    
    # build URL
    url = 'https://api.pwnedpasswords.com/range/' + hash_prefix

    # call the API
    response = call_hibp_api(url, debug)

    # parse the API response
    parsed_result = parse_password_response(hash_suffix, response, debug)
    
    # print output
    if print_output:
        if parsed_result:
            print('This password has been pwned ' + str(parsed_result) + ' times!')
        else:
            print('This password has not been pwned yet.')

    # return results
    if return_output:
        if parsed_result:
            return True # pwned
        else:
            return False # not pwned


# -----------------------------------------------------------------------------
# Parse password response
# -----------------------------------------------------------------------------
def parse_password_response(hash_suffix, response, debug=False):
    # check response code
    if not response.status_code == 200:
        print('Error reaching API')
        if debug:
            print('Response code: ' + str(response.status_code))
        exit()
    else:
        if debug:
            print('Response code: ' + str(response.status_code))

    buf = StringIO(response.text) # build text parser
    line = buf.readline().strip() # get first line of response
    
    # iterate thruogh response text
    while line:
        # split line at colon
        line_suffix, count = line.split(':', 1)
        
        # if the input hash suffix matches the hash suffix for this line
        if hash_suffix.upper() == line_suffix.upper():
            # returns the count
            return count

        # get next line
        line = buf.readline().strip()
    # returns False if the suffix does not match    
    return False



# -----------------------------------------------------------------------------
# Generate random password that has not been compromised
# -----------------------------------------------------------------------------
def generate_password(debug=False, print_output=True, return_output=False):
    while True: # loop it
        
        # generate random password
        password = passgenerator.generate()

        # check if password has been pwned
        if password_pwnage(password, debug=debug, print_output=False, return_output=True):
            if debug:
                print('Generated pwned password: ' + str(password))
            continue
        else: # false for not being pwned
            break

    # if we get here, the password has not been compromised
    if print_output:
        print(password)
    
    if return_output:
        return password



# -----------------------------------------------------------------------------
# Configure argument parser
# -----------------------------------------------------------------------------
def parse_arguments():
    # create parser object
    parser = argparse.ArgumentParser(description='Checks passwords against ' + \
                                    'the Have I Been Pwned database\n' + \
                                    'https://haveibeenpwned.com',
                                    epilog="optional arguments '-p/--password'" + \
                                    " and '-r/--prompt' cannot be used together")

    # setup arugment for handling accounts
    parser.add_argument('-a', '--account', dest='account', metavar='<account>',
                        action='store', help='account to check against database')
    
    # setup arugment for creating password
    parser.add_argument('-g', '--generate', dest='generate',
                        action='store_true', help='generate a random password that ' + \
                        'has not been compromised')

    # setup argument for handling passwords
    parser.add_argument('-p', '--password', dest='password', metavar='<password>',
                        action='store', help='password to check against database')
    
    # setup argument for prompting for password
    parser.add_argument('-r', '--prompt', dest='prompt', action='store_true',
                        help='prompt for pass to check against database')

    # setup argument for debug output
    parser.add_argument('-v', '--verbose', action='store_true', dest='debug',
                        help='verbose output, useful for debugging issues')
    
    # parse the arguments
    args = parser.parse_args()
    
    return args, parser



# -----------------------------------------------------------------------------
# Run main
# -----------------------------------------------------------------------------
def __run_main():
    args, parser = parse_arguments()

    if args.prompt and args.password:
        print("Error: Arguments '-p/--password' and '-r/--prompt' cannot be used together.")
        exit()
    
    if args.password:
        password_pwnage(args.password, debug=args.debug)

    if args.prompt:
        input_password = getpass.getpass('Password to check: ')
        password_pwnage(input_password, debug=args.debug)

    if args.account:
        account_pwnage(args.account, debug=args.debug, truncate_reponse=False)
    
    if args.generate:
        generate_password(debug=args.debug)
    
    if not args.account and not args.password and not args.prompt and not args.generate:
        parser.print_help()



# -----------------------------------------------------------------------------
# Run interactively
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    __run_main()

