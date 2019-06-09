# rgb2bgr
# Credits to KironDevCoder for making this

def tuple(t):
        return (t[2], t[1], t[0])

def dict(d):
        new_d = {}
        for index in d:
                new_d[index] = tuple(d[index])
        return new_d
