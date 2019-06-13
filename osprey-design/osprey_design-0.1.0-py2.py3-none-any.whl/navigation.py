import urwid

from .globals import ATTR_HEADER

_loop = None
_frame = None
_nav_stack = []
_options = []
_original_header = urwid.AttrMap(urwid.Padding(urwid.Text('Osprey Design Tool', align='left')), ATTR_HEADER)
_original_footer = None


def _has_back_button(): return len(_nav_stack) > 1


def _get_header_text():
    options = ['F8 to exit']
    if _has_back_button():
        options.append('F6 to go back')

    options += _options
    return 'Osprey Design Tool ' + '(' + ', '.join(options) + ')'


def add_additional_key_option(option: str):
    _options.append(option)


def _reset_options():
    _options.clear()


def _check_for_exit(key):
    if key == 'f8':
        raise urwid.ExitMainLoop()
    if key == 'f6' and _has_back_button():
        pop_page()


def _set_header_footer(page):
    _original_header.base_widget.set_text(_get_header_text())
    if hasattr(page, 'header'):
        _frame.contents['header'] = (page.header, _frame.options())
    else:
        _frame.contents['header'] = (_original_header, _frame.options())

    if hasattr(page, 'footer'):
        _frame.contents['footer'] = (page.footer, _frame.options())
    else:
        _frame.contents['footer'] = (_original_footer, _frame.options())


def init():
    global _loop
    global _frame
    _frame = urwid.Frame(urwid.SolidFill())
    _loop = urwid.MainLoop(_frame)
    _loop.unhandled_input = _check_for_exit
    return _loop


def get_loop():
    return _loop


def push_page(page):
    _reset_options()
    if issubclass(type(page), urwid.Frame):
        _loop.widget = page
        _nav_stack.append(page)
        return

    _frame.contents['body'] = (page, _frame.options())
    _nav_stack.append(page)
    _set_header_footer(page)


def pop_page():
    _reset_options()
    current_page = _nav_stack.pop()
    if issubclass(type(current_page), urwid.Frame):
        _loop.widget = _frame

    _frame.contents['body'] = (_nav_stack[-1], _frame.options())
    _set_header_footer(_nav_stack[-1])
    return current_page
