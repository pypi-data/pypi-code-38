from geocelery import Function

def f1():
    time.sleep(1)

def f2():
    return 1/0


if __name__ == "__main__":
    taskid = Function.start(f1)
    print(taskid)

    rst = Function.result(taskid)
    print(rst)