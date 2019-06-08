import pyperclip


from sget.config import CONFIG
from sget.prompt import prompt
from sget.snippet import Snippet
from sget.storage import Storage, AmbiguousNameError, SnippetNotFoundError
from sget import tty


STORAGE = Storage(CONFIG.snippet_file)


def get_all(group=None):
    collection = STORAGE.get_all_snippets()
    if group is not None:
        return collection.get_group(group)
    return collection


def add(content, description, name, groups):
    STORAGE.add_snippet(content, description, name, groups)


def fadd(snippet_file, description, name, groups):
    STORAGE.add_snippet(''.join(snippet_file.readlines()),
                        description,
                        name,
                        groups)


def edit_snippets():
    tty.edit(CONFIG.snippet_file)


def install(snippets_file):
    errors = STORAGE.install_from_file(snippets_file)
    return errors


def run(name=None):
    snippet = _get_snippet(name)
    if Snippet.is_template:
        content = prompt.fill_template(snippet.content)
        snippet = Snippet(content,
                          name=snippet.name,
                          description=snippet.description,
                          groups=snippet.groups)

    tty.put_text(snippet.content)


def cp(name=None):
    snippet = _get_snippet(name)
    _snippet_to_clipboard(snippet)


def rm(name=None):
    snippet = _get_snippet(name)
    STORAGE.rm_snippet(snippet.name)


def clear():
    STORAGE.clear_snippets()


def _get_snippet(name=None):
    if not name:
        snippet = _query_snippet()
    else:
        try:
            snippet = STORAGE.get_snippet(name)
        except AmbiguousNameError:
            snippet = _query_snippet()
    return snippet


def _snippet_to_clipboard(snippet):
    pyperclip.copy(snippet.content)


def _query_snippet():
    snippets = STORAGE.get_all_snippets()
    snippet = prompt.select_snippet(snippets)
    if not snippet:
        raise SnippetNotFoundError()
    return snippet
