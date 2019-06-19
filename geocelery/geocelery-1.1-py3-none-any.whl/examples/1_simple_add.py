from geocelery import Function

def add(x, y):
    return x + y


if __name__ == "__main__":
    taskid = Function.start(add, args=(1, 2))
    print(Function.result(taskid))