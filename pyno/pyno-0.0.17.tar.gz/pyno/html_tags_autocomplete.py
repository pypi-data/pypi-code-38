"""
This file defines a dummy class html_tag_list, used to provide auto-completion of TreeSeed

Custom tags can be added to the list, and running the script.
# The script will then self modify to update the static class declaration
# following the comment line: # Auto generated class definition
# The static definition is needed in order for autocomplete to pick it up.
"""

tags = 'body title div p h1 h2 h3 h4 h5 h6 u b i s a em strong span font del_ ins ul ol li dd dt dl ' \
       'article section nav aside header footer audio video object_ embed param fieldset legend button textarea ' \
       'label select option table thead tbody tr th td caption blockquote cite q abbr acronym address meta link ' \
       'br hr input_ img code samp pre var kbd dfn' \
       + 'plot datatable graphics html head style script'

def definition_generator(tags):
    classdef = ''

    # This code adds the static class definition
    classdef += 'class HTMLTagList:\n'
    classdef += ' '*4 + '''"""Dummy class used to provide autocomplete for TreeSeed"""\n'''
    for tag in tags.split():
        classdef += ' '*4 + tag + ' = None\n'
    return classdef


def rebuild_content(content):  # pragma: no cover
    # This code reloads the defining code from the file.
    classdef = ''
    with open(__file__) as f:
        for line in f:
            if line.startswith('# Auto generated class definition'):
                break
            else:
                classdef += line
    classdef += '# Auto generated class definition\n'
    classdef += content
    with open(__file__, 'w') as f:
        f.write(definition_generator())


if __name__ == '__main__':  # pragma: no cover
    rebuild_content(definition_generator(tags))


# Auto generated class definition
class HTMLTagList:
    """Dummy class used to provide autocomplete for TreeSeed"""
    body = None
    title = None
    div = None
    p = None
    h1 = None
    h2 = None
    h3 = None
    h4 = None
    h5 = None
    h6 = None
    u = None
    b = None
    i = None
    s = None
    a = None
    em = None
    strong = None
    span = None
    font = None
    del_ = None
    ins = None
    ul = None
    ol = None
    li = None
    dd = None
    dt = None
    dl = None
    article = None
    section = None
    nav = None
    aside = None
    header = None
    footer = None
    audio = None
    video = None
    object_ = None
    embed = None
    param = None
    fieldset = None
    legend = None
    button = None
    textarea = None
    label = None
    select = None
    option = None
    table = None
    thead = None
    tbody = None
    tr = None
    th = None
    td = None
    caption = None
    blockquote = None
    cite = None
    q = None
    abbr = None
    acronym = None
    address = None
    meta = None
    link = None
    br = None
    hr = None
    input_ = None
    img = None
    code = None
    samp = None
    pre = None
    var = None
    kbd = None
    dfnplot = None
    datatable = None
    graphics = None
    html = None
    head = None
    style = None
    script = None
