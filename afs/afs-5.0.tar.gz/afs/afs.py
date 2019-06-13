import requests, json
import datetime as dt
from time import sleep
import random as r
import errno



def uID(value='yes'):
    if value == 'yes':
        # generate randomrandomrandomrandomrandomrandomrandomrandom numbers for unique users
        a = r.randint(r.randint(r.randint(1, 1000000), r.randint(1000001, 1000000000)), r.randint(r.randint(1000000001, 1000000000000), r.randint(1000000000000, 1000000000000000)))
        b = r.randint(r.randint(r.randint(1, 1000000), r.randint(1000001, 1000000000)), r.randint(r.randint(1000000001, 1000000000000), r.randint(1000000000000, 1000000000000000)))
        c = r.randint(r.randint(r.randint(1, 1000000), r.randint(1000001, 1000000000)), r.randint(r.randint(1000000001, 1000000000000), r.randint(1000000000000, 1000000000000000)))
        random = str(a)+":"+str(b)+":"+str(c)

        # writing into txt file, reading first line every time user calls the function, and deleting the second line
        file = open("unique_id.txt", "w")
        file.write(random)
        #file.write("\n")
        print('Your Unique Number is --- ', random)
        print('Write this UID to AFS Bot on messenger for verification.')
    else:
        print("Please pass 'yes' parameter to uID function to generate your unique id")

def api(json_dump):

    '''
     Function for collection of the provided variables and strings and sending them combined as a 'GET' request
     to be distributed by Flask server later on.
        Takes one argument - 'json_dump', that basically is a stringified combination of dictionaries.
    '''

    # declare endpoint_url for GET request
    endpoint_url = "https://awayfromserver.herokuapp.com/"

    # send GET request, followed by json_dump argument
    requests.post(endpoint_url, json_dump)




def teller(iteration='default', distribution='default', maxiter='default', epochdistribution='default', epoch='default', testloss='default', valloss='default', maxdelay='default', maxdelaydelta='default', maxdelaymessage='default'):

    '''
        'teller' function takes maximum of 14 arguments. Default values are 0's.

        $iteration argument is for counting iterations. type = number.

        $distribution argument is basically a divider, for every how many iterations do you need to send the GET request. type = number.

        $maxiter is a maximum of iterations, after which the model finishes training. Make sure to send +1, as long as
        python takes the 'y' from range(x , y) and finishes the loop when technically y = (y - 1). type = number.

        $epochdistribution is the same as 'distribution' argument, but for epochs. type = number.

        $epoch counts epochs. type = number.

        $testloss takes test loss as an information. type = number.

        $valloss takes validation loss as an information. type = number.

        $maxdelay is maximum amount of delay, after which server will automatically tell you that something might be crashed,
        and you've to check the server. type = number.

        $maxdelaydelta is a maximum dynamic change of maxdelay. For instance, if maxdelay = 5 (5 seconds), and maxdelaydelta = 1,
        you won't be notified until the request is delayed for more than 6 seconds.
        In case you're saving checkpoint for every certain number of iterations, and it takes longer time than average iteration
        time, that's where you use 'maxdelaydelta' argument. type = number.


    '''
    try:
        f = open("unique_id.txt", "r")
        random = f.read()

    except FileNotFoundError:
        print("Please pass 'yes' parameter to uID function to generate your unique id")

    if iteration != 'default' and distribution != 'default' and maxiter != 'default':
        # check if iteration != 0, and != maxiter, and iteration % distribution = 0.
        if iteration != 0 and iteration <= maxiter and iteration%distribution == 0:
            json_dump = json.dumps([{'Quantity':'3'},{'Iteration':iteration}, {'Unique ID':random}])
            api(json_dump)
        # check if epoch != 0, and iteration != maxiter, and epoch % epochdistribution = 0.
        elif epoch != 0 and iteration <= maxiter and epoch%epochdistribution == 0:
            json_dump = json.dumps([{'Quantity':'5'}, {'Epoch':epoch}, {'TestLoss':testloss}, {'ValLoss':valloss}, {'Unique ID':random}])
            api(json_dump)
        # check if iteration != 0, and != maxiter, and iteration % distribution = 0, epoch != 0, epoch % epochdistribution = 0.
        elif iteration != 0 and iteration <= maxiter and iteration%distribution == 0 and epoch != 0 and epoch%epochdistribution == 0:
            json_dump = json.dumps([{'Quantity':'6'}, {'Iteration':iteration}, {'Epoch':epoch}, {'TestLoss':testloss}, {'ValLoss':valloss}, {'Unique ID':random}])
            api(json_dump)
        # check if iterations = maximum amount of iterations, i.e. "training the model has been finished"
        if iteration == maxiter:
            json_dump = json.dumps([{'Quantity':'7'}, {'Iteration':iteration}, {'Epoch':epoch}, {'MaxIter':'Training model has been finished.'}, {'TestLoss':testloss}, {'ValLoss':valloss}, {'Unique ID':random}])
            api(json_dump)
    else:
        print("You're not passing Iteration, Distribution and Maxiter variables correctly. Requests won't be sent.")

if __name__ == '__main__':
    import requests, json
    import datetime as dt
    from time import sleep
    import random as r
    
    # declare endpoint_url for GET request
    endpoint_url = "https://awayfromserver.herokuapp.com/"

