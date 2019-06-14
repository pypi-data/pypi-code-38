# text colors.
C_START_GREEN = '\33[92m'
C_START_RED = '\33[91m'
C_START_ORANGE = '\33[93m'
C_START_VIOLET = '\33[95m'
C_START_BLUE = '\33[94m'
C_START_GREY = '\33[90m'
# bg colors.
C_END = '\33[0m'

"""
    Put all the elements into one single string regardless of the Type of,
    individual elements.

    :param list_
        list of elements.
    :returns str
"""


def get_single_str(list_):
    list_of_strs = []
    for elem in list_:
        list_of_strs.append(str(elem))
    return ' '.join(list_of_strs)


"""
    Each print_x function acts as a normal print function in python, albeit colored.
"""
# green


def print_success(*strs):
    global C_START_GREEN
    global C_END
    print(C_START_GREEN + get_single_str(strs) + C_END)

# red


def print_err(*strs):
    global C_START_RED
    global C_END
    print(C_START_RED + get_single_str(strs) + C_END)

# yellow


def print_warning(*strs):
    global C_START_ORANGE
    global C_END
    print(C_START_ORANGE + get_single_str(strs) + C_END)

# blue


def print_primary(*strs):
    global C_START_BLUE
    global C_END
    print(C_START_BLUE + get_single_str(strs) + C_END)

# violet


def print_secondary(*strs):
    global C_START_VIOLET
    global C_END
    print(C_START_VIOLET + get_single_str(strs) + C_END)

# grey


def print_muted(*strs):
    global C_START_GREY
    global C_END
    print(C_START_GREY + get_single_str(strs) + C_END)
