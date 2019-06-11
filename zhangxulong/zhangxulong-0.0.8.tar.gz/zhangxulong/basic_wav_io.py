import soundfile as soundfile


def wavread(filename):
    x, fs = soundfile.read(filename)
    return x, fs


def wavwrite(filename, y, fs):
    soundfile.write(filename, y, fs)
    return 0



