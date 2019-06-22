VERSION_SEPARATOR = "."
TAG_SEPARATOR = "/"
URL_SEPARATOR = "|"

def isValidStr(string):
    if string.count(VERSION_SEPARATOR) == 0 and \
       string.count(TAG_SEPARATOR) == 0 and \
       string.count(URL_SEPARATOR) == 0:
        return True
    else:
        return False

def invalidChars():
    return VERSION_SEPARATOR + TAG_SEPARATOR + URL_SEPARATOR