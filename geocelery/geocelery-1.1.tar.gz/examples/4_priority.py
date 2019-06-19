from geocelery import Function, TaskType

def xxx(idx):
    print("**********AAA_%d**********"%idx)
    return idx*2

def yyy(idx):
    import time
    time.sleep(10)
    # open("/celery_data/%d_BBB_%d" % (idx, int(time.time())), "w").close()
    return "BBB_%d"%idx

def zzz(idx):
    import time
    time.sleep(10)
    # open("/celery_data/%d_CCC_%d" % (idx, int(time.time())), "w").close()
    return "CCC_%d"%idx

def submit_b():
    for idx in range(1000):
        Function.start(yyy, args=(idx,), tasktype=TaskType.B)

def submit_c():
    for idx in range(1000):
        Function.start(zzz, args=(idx,), tasktype=TaskType.C)

if __name__ == "__main__":
    import time, threading
    threading.Thread(target=submit_b).start()
    threading.Thread(target=submit_c).start()

    time.sleep(30)  #等待10秒，让B/C类开始执行，然后提交A类任务

    for idx in range(10):
        beg = time.time()
        taskid = Function.start(xxx, args=(idx,), tasktype=TaskType.A)
        rst = Function.result(taskid)
        print(time.time()-beg, rst)
        time.sleep(3)



