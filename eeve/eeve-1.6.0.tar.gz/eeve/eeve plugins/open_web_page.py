import webbrowser


def open_page(url: str, new: int = 0, autoraise: bool = True):
    webbrowser.open(url, new=new, autoraise=autoraise)


actions = {'open webpage': {'run': open_page}}
