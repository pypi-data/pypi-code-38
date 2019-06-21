
def strip_space_tab(string: str):
    return string.replace(' ', '').replace('\t', '')


def strip_space_tab_eol(string: str):
    return strip_space_tab(string).replace('\n', '')

# see also: https://stackoverflow.com/questions/33659074/what-the-diff-python-
# unittest-failing-due-to-leading-whitespace-in-multine
# stackoverflow user:755851


""" For HTML and XML
A better approach which I don't know how to do off the top of my head would be to
caniconalize the two strings. Clean Up HTML in Python has some suggestions, e.g.:

from BeautifulSoup import BeautifulSoup
htmlcase = BeautifulSoup(htmlcase).prettify()
htmltest = BeautifulSoup(htmltest).prettify()
"""
