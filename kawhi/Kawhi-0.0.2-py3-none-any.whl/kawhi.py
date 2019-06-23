"""
Kawhi package test pypi package publishing
"""
from support_modules.get_jokes import get_joke


def say_hello(name=None):
    """ dummy function"""
    if name:
        return f"Hello, Kawhi - This is {name}."

    return "Hello, Kawhi!"


def kawhi_joke(search_term=None):
    """
    Gets a joke and appends a Kawhi laugh to it.
    """

    if search_term:
        # TODO get joke about a specific topic
        pass

    returned_joke = get_joke()

    if not returned_joke["success"]:
        return "That's all folks!"

    # return joke:
    return f"{returned_joke['joke']}\n\nAha....ha, ha, ha, ha"


print(kawhi_joke())
