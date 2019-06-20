import re


def find_splitter(string):
    ol = r"\d+\."
    string = string.strip()
    if "\n" in string:
        sep = "\n"
    elif "," in string:
        sep = ","
    elif re.match(ol, string):
        sep = ol
    elif " " in string:
        sep = " "
    else:
        return None

    return re.compile(sep)


def str2list(content):
    """
    Input is any string. This function finds a main seperator in
    given string and split the string into parts with the main seperator
    """
    sep = find_splitter(content)
    # print("sep: \"{}\";".format(sep))
    l = []
    for part in sep.split(content):
        part = part.strip()
        if part != "":
            l.append(part)

    return l
