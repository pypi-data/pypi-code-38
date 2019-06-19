from geocelery import MapReduce

def f(num):
    if num%3==0:
        raise Exception("xxx")
    return num

def g(nums):
    return sum(nums)


if __name__ == "__main__":
    taskid = MapReduce.start(range(1, 11), f, g, ignore_error=True)
    rst = MapReduce.result(taskid)
    print(rst, rst==sum([x for x in range(1,11) if x%3]))


