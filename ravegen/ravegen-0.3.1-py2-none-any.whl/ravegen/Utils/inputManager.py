
_YES_ANSWERS_ = ["y","yes"]
_NO_ANSWERS_ = ["n", "no"]

def getInput(_string):
    val = raw_input(_string)
    return val

def getYesNoAnswer(_string):
    while True:
        val = raw_input(_string).lower()
        if val in _YES_ANSWERS_:
            return True
        if val in _NO_ANSWERS_:
            return False
