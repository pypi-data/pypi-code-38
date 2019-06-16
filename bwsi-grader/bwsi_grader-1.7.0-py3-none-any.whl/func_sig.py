from typing import Any, Iterable
from itertools import chain


def pad_indent(x: str, ln: int =0) -> str:
    return x.replace("\n", "\n" + " "*ln)


def form_func_sig(*args: Any, func_name: str="", **kwargs: Any) -> str:
    """
    Forms a function-signature string out of the args and kwargs.

    The returned string has nicely-formatted indentations for things
    like multi-line array reprs.

    Parameter
    ---------
    *args : Any

    func_name : str

    **kwargs : Any

    Returns
    -------
    str

    Examples
    --------
    >>> form_func_sig(2, 3, k=1, z=["apple", None], func_name="func")
    "func(2, 3, k=1, z=['apple', None])"

    >>> x = np.array([[1,2,3], [1 ,2, 3], [1,2,2]])
    >>> form_func_sig(None, x, pizza="mouse", z=x, func_name="func")
    func(None, array([[1, 2, 3],
                      [1, 2, 3],
                      [1, 2, 2]]),
         pizza='mouse', z=array([[1, 2, 3],
                                 [1, 2, 3],
                                 [1, 2, 2]]))

    >>> form_func_sig(2, func_name='f')
    "f(2)"

    >>> form_func_sig(pizza=[[], []], func_name="pizza_shop")
    'pizza_shop(pizza=[[], []])'

    >>> form_func_sig()
    '()'
    """
    assert "\n" not in func_name, "`func_name` cannot contain a newline character"

    def join(x: Iterable) -> str:
        """ Joins the reprs of the elements of `x` using the
        separator ', ' unless the repr contains a newline -
        then the separator begins a newline.
        """
        out = ""
        sep = ""
        for item in x:
            ln_break = "\n" in item
            out += sep
            if ln_break and "\n" not in sep:
                for prev in reversed(out.splitlines()):
                    item = item.replace("\n", "\n" + " "*len(prev))
                    break
            out += item
            sep = ",\n" if ln_break else ", "
        return out

    values = (f"{key}=" + pad_indent(repr(value), len(f"{key}="))
              for key, value in kwargs.items())
    sig = join(chain((repr(i) for i in args), values))
    sig = pad_indent(sig, len(func_name + "("))
    return func_name + "(" + sig + ")"
