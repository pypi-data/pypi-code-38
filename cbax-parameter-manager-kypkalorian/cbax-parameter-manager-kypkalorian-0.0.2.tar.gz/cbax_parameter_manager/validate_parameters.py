import json


def validate_parameters(args, parameters):

    for a in args:

        print(a)


        temp = a.replace("-", '')
        #print(a, end=' ')
        #print(args[a])

        if temp not in parameters:
            print(f"Unknown parameter: {temp}")
            return False


        if parameters[temp]['requires_value'] == True and len(args[a]) == 0:
            #no required value yet is true
            print(f"A value is required for argument [{temp}]")
            return False

        #Check if the current argument is allowed
        if len(parameters[temp]['allowed_values']) != 0:

            for value in args[a]:
                if value not in parameters[temp]['allowed_values']:
                    print(f"parameter value \"{value}\" for argument {a} is not found in allowed_values")
                    return False
        else:
            pass

            # don't check for allowed values
            # for value in args[a]:
            #     print("> ", end='')
            #     print(a + ": " + value)


    #no fails anyways
    for p in parameters:
        temp_p = "--" + p
        if parameters[p]['Required'] == True:
            if temp_p not in args:
                #print(p)
                print(f"required argument \"{p}\" not found")
                return False

    return True
