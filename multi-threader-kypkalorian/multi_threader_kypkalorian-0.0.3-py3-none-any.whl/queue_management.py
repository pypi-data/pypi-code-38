import time, json


def status_update(message, q):
    q.put(message)

    # status_update("getting option settings", q)
    # Basically updates the message


def queue_get_all(q):

    stuff = []

    while q.empty() == False:
        stuff.append(q.get())

    return stuff


# get last status from queue
def get_status(q):

    last = None

    while q.empty() == False:
        last = q.get()

    return last
