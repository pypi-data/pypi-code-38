""" Provides messages and warnings naming the origin """
import inspect


def warn(message, level=0):
    " https://stackoverflow.com/a/2654130/5172579 "

    curframe = inspect.currentframe()
    frame = inspect.getouterframes(curframe, 2)[1]

    if level == 0:
        typ = "Message"
    elif level == 1:
        typ = "Warning"
    elif level == 2:
        typ = "Error"

    stars = "*" + "*" * level

    file = frame[1].split("hilde")[-1]

    print(
        f"{stars} {typ} from file hilde{file}, line {frame[2]}, function {frame[3]}:"
    )
    print(f"--> {message}\n")

    if typ == "Error":
        raise RuntimeError("see above")
