"""Utilities to handle redirects and redirect histories, also some proxy info"""
import requests

ignored_domains = ["safelinks.protection.outlook.com", "can01.safelinks.protection.outlook.com"] # A list of domains to ignore in trace

def trace(url, print_response = False):
    """
    :param: url
    :type url: String

    """
    if "https://" in url: # Checks if protocols are present
        None
    if "http://" in url:
        None
    else: # Add a protocol to URL
        url = "http://" + url

    try:
        trace = requests.get(url)
    except Exception as identifier:
        if print_response == True:
            print("Error while checking {} \nError Code: {}".format(url, identifier))
        return(["Error while checking {} \nError Code: {}".format(url, identifier)])

    
    if trace.history:
        output = []
        skip_ignored_domains(trace.history)
        if (print_response == True):
            print("\nPrinting trace for {}".format(url))
        for level, redirect in enumerate(trace.history):
            output.append([level+1, redirect.url, redirect.status_code])
        output.append([len(output)+1,trace.url, trace.status_code])
        if (print_response == True):
            for redirect in output:
                print("\nRedirect level:{} \nURL: {} \nHTTP Code: {}".format(redirect[0], redirect[1], redirect[2]))
        return output
    else:
        if (print_response == True):
            print("Request was not redirected")
        return(["Request was not redirected"])

def skip_ignored_domains(response_trace):
    """
    :param: response_trace
    :type response_trace: List of responses
    :returns: The stripped list of responses
    :return_type: List of responses

    Takes a list of reponses and removes any responses that
    have domains that are in the ignored_domains variable"""
    for domain in ignored_domains:
        for count, response in enumerate(response_trace):
            if domain in response.url:
                response_trace.remove(response)
            else:
                continue
    return response_trace

if __name__ == "__main__":
    url_to_test = input("What URL should be traced?: ")
    print(trace(url_to_test, print_response=False))
