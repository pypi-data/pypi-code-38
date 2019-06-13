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
    else:
        print("Please pass 'yes' parameter to uID function to generate your unique id")

def api(json_dump):

    '''
     Function for collection of the provided variables and strings and sending them combined as a 'GET' request
     to be distributed by Flask server later on.
        Takes one argument - 'json_dump', that basically is a stringified combination of dictionaries.
    '''

    # declare endpoint_url for GET request
    endpoint_url = "https://awayfromserver.herokuapp.com"

    # send GET request, followed by json_dump argument
    requests.post(endpoint_url, json_dump)




def teller(iteration=0, distribution=0, distrmessage='', maxiter=0, maxitermessage='', epochdistribution=0, epoch=0, epochmessage='', testloss=0, valloss=0, maxdelay=0, maxdelaydelta=0, maxdelaymessage=''):

    '''
        'teller' function takes maximum of 14 arguments. Default values are 0's.

        $iteration argument is for counting iterations. type = number.

        $distribution argument is basically a divider, for every how many iterations do you need to send the GET request. type = number.

        $distrmessage - your message after reaching specific number of iterations, when iterations % distribution == 0. type = string.

        $maxiter is a maximum of iterations, after which the model finishes training. Make sure to send +1, as long as
        python takes the 'y' from range(x , y) and finishes the loop when technically y = (y - 1). type = number.

        $maxitermessage is a message you want to send after reaching maxiter size. type = string.

        $epochdistribution is the same as 'distribution' argument, but for epochs. type = number.

        $epoch counts epochs. type = number.

        $epochmessage is sended after reaching number of epochs when epochs % epochdistribution == 0 . type = string

        $testloss takes test loss as an information. type = number.

        $valloss takes validation loss as an information. type = number.

        $maxdelay is maximum amount of delay, after which server will automatically tell you that something might be crashed,
        and you've to check the server. type = number.

        $maxdelaydelta is a maximum dynamic change of maxdelay. For instance, if maxdelay = 5 (5 seconds), and maxdelaydelta = 1,
        you won't be notified until the request is delayed for more than 6 seconds.
        In case you're saving checkpoint for every certain number of iterations, and it takes longer time than average iteration
        time, that's where you use 'maxdelaydelta' argument. type = number.

        $maxdelaymessage is a message for you to receive after reaching maximum time of delay.  type = string.


    '''
    try:
        f = open("unique_id.txt", "r")
        random = f.read()
        print("Your unique ID is --- ", random)

    except FileNotFoundError:
        print("Please pass 'yes' parameter to uID function to generate your unique id")

    # check if iteration != 0, and != maxiter, and iteration % distribution = 0.
    if iteration != 0 and iteration != maxiter and iteration%distribution == 0:
        json_dump = json.dumps(str({1:{str(iteration):str(distrmessage)}, 2:{'Unique Id':str(random)}}))
        api(json_dump)
    # check if epoch != 0, and iteration != maxiter, and epoch % epochdistribution = 0.
    if epoch != 0 and iteration != maxiter and epoch%epochdistribution == 0:
        json_dump = json.dumps(str({1:{(epoch):str(epochmessage), 'Test Loss':str(testloss)}, 2:{'Validation Loss':str(valloss), 'Unique Id':str(random)}}))
        api(json_dump)
    # check if iteration != 0, and != maxiter, and iteration % distribution = 0, epoch != 0, epoch % epochdistribution = 0.
    if iteration != 0 and iteration != maxiter and iteration%distribution == 0 and epoch != 0 and epoch%epochdistribution == 0:
        json_dump = json.dumps(str({1:{str(iteration):str(distrmessage), str(epoch):str(epochmessage)}, 2:{'Test Loss':str(testloss), 'Validation Loss':str(valloss)}, 3:{'Unique Id':str(random)}}))
        api(json_dump)
    # check if iterations = maximum amount of iterations, i.e. "training the model has been finished"
    if iteration == maxiter:
        json_dump = json.dumps(str({1:{str(iteration):distrmessage}, 2:{str(epoch):str(epochmessage)}, 3:{str(maxiter):maxitermessage, 'Test Loss':str(testloss)}, 4:{'Validation Loss':str(valloss), 'Unique Id':random}}))
        api(json_dump)


if __name__ == '__main__':
    import requests, json
    import datetime as dt
    from time import sleep
    import random as r
    
    # declare endpoint_url for GET request
    endpoint_url = "https://awayfromserver.herokuapp.com"

