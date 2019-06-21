def fibonacci(n):
    if n <= 1:
        return 1
    else:
        return fibonacci(n-2)+fibonacci(n-1)


fibonacci(0)
fibonacci(20)


