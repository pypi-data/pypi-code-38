#!/usr/bin/env python
"""
Tools functions
"""

def check_params_exist(params_list, event, event_attribute=None, is_cfn=False):
    """
    Checks that parameters in event exist

    Depending on the type of call to the Lambda function,
    checks if all the input parameters are present

    Args:
    ----------
      params_list: list
        List of parameters to check the presence in event
      event: dict
        Lambda function handler event dict
      event_attribute: string
        Name of the attribute to check if parameters are
        stored within that key of the event dict
      is_cfn: bool
        Specifies if the caller is CloudFormation and
        therefore lookup into ResourceProperties key of event

    Returns
    ------
    tuple
        0 - bool to inform if the task is successful or failed
        1 - string describing which parameter is missing or to say all params have been found

    """
    event_lookup = None
    if is_cfn and not event_attribute:
        event_lookup = "ResourceProperties"
    elif not is_cfn and event_attribute:
        if not event_attribute in event.keys():
            raise AttributeError("Event does not have key {0}".format(event_attribute))
        event_lookup = event_attribute
    if not event_lookup:
        for param in params_list:
            if not param in event.keys():
                raise AttributeError("{0} not in events attributes".format(param))
    else:
        print(event_lookup)
        print(event[event_lookup])
        for param in params_list:
            print(param)
            if not param in event[event_lookup].keys():
                raise AttributeError("{0} not in events attributes".format(param))
    return True
