import logging
import string


# timeNow is used to update things based on how much time has passed.
# Note: on Windows, time.clock() is more precise than time.time()
# On Windows time.clock() also does not change when the system clock changes.
# On linux however, time.clock() measures process time rather than wall time.
import platform
if platform.system() == 'Windows':
    from time import clock as timeFunction
else:
    from time import time as timeFunction


def timeNow():
    '''
    This function exists so that even things which get a reference to timeNow()
    at import time can still be fooled by patching timeFunction.
    '''
    return timeFunction()


def new(count):
    '''new(count) - returns an iterator object which will give count distinct
    instances of the object class.  This is useful for defining setting
    options.  For example, north, south, east, west = new(4) . There is no
    reason that these options should be given numeric values, but it is
    important that north != south != east != west.
    '''
    for i in range(count):
        yield object()


def initLogging(debug=False, logFile=None, prefix=''):
    import twisted.logger
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter(
        '%(asctime)s {prefix}%(message)s'.format(prefix=prefix)))
    logging.getLogger().addHandler(h)
    if logFile:
        h = logging.FileHandler(logFile)
        h.setFormatter(logging.Formatter(
            '%(asctime)s {prefix}%(message)s'.format(prefix=prefix)))
        logging.getLogger().addHandler(h)
        logging.info('Initialised logging.')

    # Remove asyncio debug and info messages, but leave warnings.
    logging.getLogger('asyncio').setLevel(logging.WARNING)

    observer = twisted.logger.STDLibLogObserver()
    twisted.logger.globalLogPublisher.addObserver(observer)


# Convenience functions for wrapping long strings based on maximum pixel width
# http://www.pygame.org/wiki/TextWrapping

def truncline(text, font, maxwidth):
    real = len(text)
    stext = text
    l = font.size(text)[0]
    cut = 0
    a = 0
    done = 1
    while l > maxwidth:
        a = a + 1
        n = text.rsplit(None, a)[0]
        if stext == n:
            cut += 1
            stext = n[:-cut]
        else:
            stext = n
        l = font.size(stext)[0]
        real = len(stext)
        done = 0
    return real, done, stext


def wrapline(text, font, maxwidth):
    done = 0
    wrapped = []

    while not done:
        nl, done, stext = truncline(text, font, maxwidth)
        wrapped.append(stext.strip())
        text = text[nl:]
    return wrapped


class BasicContextManager(object):
    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        pass


def stripPunctuation(nick):
    exclude = set(string.punctuation + ' ')
    return ''.join(ch for ch in nick if ch not in exclude)
