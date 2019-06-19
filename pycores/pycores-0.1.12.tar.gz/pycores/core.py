# Insert your code here. 

'''
Usage

@static_vars(counter = 0)
def foo():
    foo.counter += 1
'''
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


def encodeid(number):
    """
    number to b64/b16 str

    :param number:
    :return:
    """
    strs = str(number)
    bstr = strs.encode('utf-8')
    bstr = base64.b64encode(bstr)
    # bstr = base64.b16encode(bstr)
    return bstr.decode('utf-8')

def decodeid(s):
    '''
    b64/b16 str to number
    :param s:
    :return:
    '''
    bstr = base64.b64decode(s.encode("utf-8"))
    # bstr = base64.b16decode(s.encode("utf-8"))

    return int(bstr)