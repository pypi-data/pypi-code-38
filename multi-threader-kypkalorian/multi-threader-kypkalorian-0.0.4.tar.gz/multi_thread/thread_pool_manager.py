from multiprocessing import Process, Manager, Value, Queue

import os, sys, time, json, datetime, random

from .display_v2 import display
from .queue_management import get_status
from .thread_worker import thread_worker

#========================================================================================================>
#========================================================================================================>
#================================== Multi processor right here ==========================================>
#========================================================================================================>
#========================================================================================================>


def thread_pool_manager(ListToProcess=None, s_timeout=None, m_processes=None, kwargs=None, display_bool=True, function=None):

    #Stuff here
    p_list              = {} # dict that holds process list
    q_list              = {} # dict that holds communications queues
    latest_status       = {}
    more_data           = True
    status              = ''
    cont                = True
    manager             = Manager()
    shared_results      = manager.dict()
    list_size           = len(ListToProcess)
    exception_list      = []
    longest_env_name    = 0
    index_of_longest    = 0
    list_pointer        = 0
    bool_prod           = False
    disp_mod            = 0
    # Manager loop
    while cont or more_data:

        # add more tasks to the list - max processes used here
        while len(p_list) < m_processes:
            #print("attempting to add another process")

            if list_pointer >= list_size:
                #print("no more processes in the list!")
                more_data = False
                break
            else:

                current_list_item = ListToProcess[list_pointer]

                #print(current_list_item)
                q_list[current_list_item['Key']] = Queue()     # Status Queue            # Current item      # shared results    # process timeout   # kwargs
                p = Process(target=thread_worker, args=(q_list[current_list_item['Key']], current_list_item, shared_results, s_timeout, kwargs, function) )
                init_time = time.time()
                p.start()
                p_list[current_list_item['Key']] = (p , init_time)
                list_pointer = list_pointer + 1
                #dict should have a bigger size now

        cont = False

        time.sleep(.05)

        deletion_list = []

        # CHECK IF PROCESSES ARE FINISHED
        for proc in p_list:
            if p_list[proc][0].is_alive():
                cont = True #if any process is still alive set this flag to true
            else:
                try:
                    p_list[proc][0].join()
                    #print("PROC " + str(proc))
                    deletion_list.append(proc)
                    #print(f"Finished Job: {proc}")
                except:
                    print("failed to join this thread. Didn't delete it either.")
                    #input("fuck")

        # remove processes that have been joined. I don't know what problems this could have if I delete my reference to a process that fails to join but isn't aliveself.
        # Problems could arise like having 5 blocked processes. No timeout mechanism either.
        # DELETING PROCESSES THAT HAVE FINISHED. You can't modify the data structure during iteration, at least you can't delete elements from it.
        for p in deletion_list:
            del p_list[p]
            del q_list[p]

        # def get_status(q):
        for q_item in q_list:
            temp = get_status(q_list[q_item])

            if temp == None:
                pass
            else:
                latest_status[q_item] = temp

        disp_mod += 1

        try:
            pass
            if display_bool:
                #only display every 50 iterations. Done because I lowered the delay between each loop 
                if disp_mod % 50 == 0:
                    display(p_list, latest_status, str(list_pointer) + "/" + str(list_size), m_processes, s_timeout, bucket=None)
        except Exception as e:
            print(e)
            pass

    new_dict = {}
    for item in shared_results:

        new_dict[item] = shared_results[item]

    return new_dict
    #-----END WHILE-------------------------------------------------------->
