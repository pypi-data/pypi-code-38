import tempfile
import webbrowser
import os
import __main__
from bs4 import BeautifulSoup

def html_prettify(html):
    return BeautifulSoup(str(html), 'html.parser').prettify()


def browser_preview(page, dir=None, prettify=True):  # pragma: no cover
    """ Creates a temporary html file with the string_content, and opens it in a browser
    The script then waits for user input and when entered cleans up the temporary file

    set dir=False to use system default location for temporary file.
        dir=None puts file in current directory, to allow relative links to work in testing

    prettify sets if the output should be pretty parsed html or just straight output. Defaults to True, which uses
    BeautifulSoup.prettify to structure html in a nice human readable format
    """

    if prettify:
        convert = html_prettify
    else:
        convert = str
    with tempfile.NamedTemporaryFile(suffix='.html',
                                     delete=True,
                                     dir=os.path.dirname(__main__.__file__) if dir is None
                                     else (None if dir is False else dir)) as file:
        file.write(convert(page).encode('utf-8'))
        print(convert(page).encode('utf-8'))
        file.flush()

        print(r'file:\\' + file.name)

        webbrowser.open(r'file:///' + file.name.replace('\\', '/'))
        input("Press Enter to end script and clean up temporary file...")
