from geocelery import Function, State

def add(x, y):
    import time
    time.sleep(3)
    return x + y


if __name__ == "__main__":
    taskid = Function.start(add, args=(1, 1)) #add(1, 1)

    print(Function.status(taskid))

    import time
    time.sleep(5)

    print(Function.status(taskid) == State.SUCCESS)

    print(Function.result(taskid))
