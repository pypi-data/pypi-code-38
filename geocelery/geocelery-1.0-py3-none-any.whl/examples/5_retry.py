from geocelery import Function

def xxx():
    import os
    if os.path.exists("/mnt/celery/retry_ces.txt"):
        return "hello,world"
    else:
        open("/mnt/celery/retry_ces.txt", "w").close()
        raise Exception()

if __name__ == "__main__":
    taskid = Function.start(xxx)

    print(Function.status(taskid)) #重试之后成功，状态为RETRY
    print(Function.result(taskid))





