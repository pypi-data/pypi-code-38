from geocelery import MapReduce

def f(num):
    return num * num

def g(nums):
    return sum(nums)

if __name__ == "__main__":
    taskid = MapReduce.start(range(1, 11), f, g)
    rst = MapReduce.result(taskid)
    print(rst, rst==sum([x*x for x in range(1,11)]))