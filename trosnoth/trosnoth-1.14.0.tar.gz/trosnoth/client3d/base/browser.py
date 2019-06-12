import webbrowser


def openPage(app, url):
    # Open in a new tab if possible.
    try:
        webbrowser.open_new_tab(url)
    except AttributeError:
        webbrowser.open_new(url)
