import json, os, time, datetime

max_name_len = 65
#---------------------------------------------------------------------------------------------------->
#------------------------------------------ Display ------------------------------------------------->
#---------------------------------------------------------------------------------------------------->
def sp(num):

    count = 0
    while True:
        print(" ",end = '')
        count = count + 1

        if count >= num:
            break

    pass


# get last status from queue
def get_status(q):

    last = None

    while q.empty() == False:
        last = q.get()

    return last



def display(info, statuses, progress, max_processes=None, timeout=None, bucket=None):
    print(" ")
    print(" ")



    numItems = len(info)

    width = max_processes

    cur = time.time()

    os.system('clear')
    print(" ")
    print("<=== Running Jobs ==================>\n")
    #print("====================================>")
    counter = 0
    for item in info:
        wordlen     = len(str(item))
        worddiff    = max_name_len - wordlen
        #worddiff2   = max_name_len - wordlen

        print(item, end='')
        sp(worddiff) #worddiff

        temp2 = statuses[item]
        #print(f"temp2: {temp2}", end='')
        worddiff2 = 25 - len(temp2)
        try:


            sp(worddiff2)
            #print(len(worddiff2))

            print(temp2, end='')
        except Exception as e:
            print(e, end='')
            pass

        #Calculating duration
        st = info[item][1]
        dur = cur - st

        try:
            #print 5 digits of duration
            #sp(worddiff2) # Print a number of spaces to make an even go at it here
            print('\t', end='')

            print(str(dur)[0:5], end='')
            print("s")
        except:
            print(dur)
    diff = width - numItems
    for i in range(0,diff):
        print("[                           ]")
    print("\n<=========================================>")
    #print("Environment: " + str(bucket))
    print("timeout " + str(timeout))
    print('processes ' + str(max_processes))
    print('Started: ' + progress)
    print(" ")

    time.sleep(.25)
