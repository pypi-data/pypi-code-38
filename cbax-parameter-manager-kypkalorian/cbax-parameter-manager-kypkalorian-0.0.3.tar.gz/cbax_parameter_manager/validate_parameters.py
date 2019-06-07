import json


def validate_parameters(args, parameters_list):

    parameters = {}

    # Rebuild list into dict for validation
    for p in parameters_list:
        parameters[p['name']] = p

    for idx, a in enumerate(args):

        temp = a.replace("-", '')

        if temp not in parameters:
            print(f"\nUnknown parameter: {temp}")
            return False

        if parameters[temp]['requires_value'] == True and len(args[a]) == 0:
            #no required value yet is true
            print(f"\nA value is required for argument [{temp}]")
            return False

        #Check if the current argument is allowed
        if len(parameters[temp]['allowed_values']) != 0:

            for value in args[a]:
                if value not in parameters[temp]['allowed_values']:
                    print(f"\nparameter value \"{value}\" for argument {a} is not found in allowed_values")
                    return False
        else:
            pass
    #no fails anyways
    for p in parameters:
        temp_p = "--" + p
        temp_n = "-" + p
        if parameters[p]['Required'] == True:
            if temp_p not in args:
                if temp_n not in args:
                    print(f"\nrequired argument \"{p}\" not found")
                    return False

    return True
