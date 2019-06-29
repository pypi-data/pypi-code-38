import time
import traceback


def makeFunctions(functions, breakTime=None, params=None):
    startTime = time.time()
    while True:
        try:
            for function in functions:
                function(params)
            break
        except:
            if breakTime is not None and time.time() - startTime > breakTime:
                print("Too match wait, Error:\n", traceback.format_exc())
                return False
            continue
    return True


def getWithFunction(function, getElem, breakTime=None):
    startTime = time.time()
    elem = None
    while True:
        try:
            elem = function(getElem)
            break
        except:
            if breakTime is not None and time.time() - startTime:
                print("Too match wait, Error:\n", traceback.format_exc())
                break
            print(traceback.format_exc())
    return elem
