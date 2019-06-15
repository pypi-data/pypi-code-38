import re

YYYYMMDD = re.compile("20\d{2}\d{2}\d{2}[/_-]")
YYYY_MM_DD = re.compile("20\d{2}[/_-]\d{2}[/_-]\d{2}[/_-]")
YYYY_MM = re.compile("20\d{2}[/_-]*\d{2}[/_-]")
YYYY = re.compile("[/_-]20\d{2}[/_-]")


def re_count(char, min_count, max_count):
    """ example that can help validating urls with a set number of e.g. dashes or slashes """
    min_count = str(min_count)
    max_count = str(max_count)
    r = "^" + "([^{0}]*{0}[^{0}]*)".format(char) + "{" + min_count + "," + max_count + "}" + "$"
    return re.compile(r)


def make_regex(x):
    if isinstance(x, str):
        return re.compile(x)
    return x
