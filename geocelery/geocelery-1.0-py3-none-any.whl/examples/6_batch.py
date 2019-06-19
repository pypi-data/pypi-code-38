import time
from celery.states import SUCCESS
from geocelery import BatchFunction

def xxx(x):
    import time
    print("------------%d------------"%x)
    time.sleep(10)
    print("++++++++++++%d++++++++++++"%x)

taskid = BatchFunction.start(xxx, range(100))

beg = time.time()
while True:
    status = BatchFunction.status(taskid)
    if status == SUCCESS:
        print(time.time()-beg)
        break
    print(status)
    time.sleep(1)