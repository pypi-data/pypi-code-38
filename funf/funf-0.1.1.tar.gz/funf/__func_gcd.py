def GCD(x, y):
    if y == 0:
        return x
    else:
        GCD(y, x % y)
