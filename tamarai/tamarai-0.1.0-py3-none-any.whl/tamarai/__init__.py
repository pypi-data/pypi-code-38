import random
import time

# colors:
COLOR_END = "\033[0m"
COLOR_GREEN = "\033[94m"

# abanibi chars:
ABANIBI = ("a", "e", "i", "o", "u")
ADDED_CHAR = "b"


def baklava():
    return "yay"


def fib(x):
    """
    :returns an array of first x fib numbers
    :param x: length of to-be-found array
    :return: array of first x fib numbers
    """
    if type(x) != int:
        raise Exception("Input variable must be a positive int")
    if x < 0:
        raise Exception("Input variable must be a positive int")
    result = []
    a = 0
    b = 1
    c = 1
    while len(result) != x:
        result.append(a)
        a = b
        b = c
        c = a + b
    return result


def lineprnt(sentence):
    result = ""
    sentence = sentence.upper()
    for i in sentence:
        result += i + "\n"
    return result


def yesno():
    choices = (
        "Maybe",
        "Yes",
        "No",
        "Probably",
        "Probably not",
        "Perhaps",
        "Nah",
    )
    return random.choice(choices)


def selfdestruct(close=False):
    print("Initiating self destruct sequence . . .")
    animation = "|/-\\"
    for i in range(30 + random.randint(0, 15)):
        print(end="\r")
        print(animation[i % len(animation)], end="")
        time.sleep(0.1)
    print("\rDone, closing all baklava processes", end="")
    if close:
        quit()


def laser(sec=20):
    spaces = ""
    for i in range(sec):
        spaces += " "
        print(end="\r")
        print(COLOR_GREEN + spaces + "-" + COLOR_END, end="")
        time.sleep(0.1)
    print("\r", end="\r")


def abanibi(string):
    out = ""
    for letter in string:
        if letter in ABANIBI:
            out += letter + ADDED_CHAR + letter
        else:
            out += letter
    return out


if __name__ == '__main__':
    # selfdestruct()
    # laser(40)
    print(abanibi("ani ohev otach"))
