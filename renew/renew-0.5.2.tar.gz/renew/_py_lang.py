import re
from collections import OrderedDict

import six

PY_IDENTIFIER_VALIDATOR = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)

PY_FILE_HEADER = u"""\
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file has been created with renew.
# A py-pickling tool: https://pypi.org/project/renew/

"""


def build_py_file_content(ordered_name_value_pairs, ref_watches=None, all_refs=False):
    dependencies_list = []  # is being filed while recursive traverse of dispatch_repr

    if all_refs and ref_watches:
        if not isinstance(ref_watches, dict):
            raise TypeError("Bad ref_watches type. Expecting dict, got %s." % type(dict).__name__)
        rdl = [("." + sub_module_name(n), n) for n in ref_watches.values()]
        dependencies_list.extend(rdl)

    code = render_code(ordered_name_value_pairs, dependencies_list, ref_watches)
    imports = render_imports(dependencies_list)

    return PY_FILE_HEADER + imports + code


def render_code(ordered_name_value_pairs, dependencies_list, ref_watches):
    validate_objects(ordered_name_value_pairs)
    code_snippets = []

    for reference_name, single_object in ordered_name_value_pairs:
        snippet = u"".join(dispatch_repr(single_object, dependencies_list, True, references=ref_watches))
        code_snippets.append(u"{} = {}\n".format(reference_name, snippet))

    return "\n".join(code_snippets)


def render_imports(dependencies_list):
    def make_import(src, namespace):
        if src:
            return u"from {} import {}\n".format(src, namespace)
        else:
            return u"import {}\n".format(namespace)

    def key(item):
        s, n = item
        rank = 0 if not s or not s.startswith(".") else 1
        return rank, s or n

    sorted_ = sorted(dependencies_list, key=key)
    return "".join(make_import(*d) for d in sorted_) + "\n"


def dispatch_repr(object_, dep_list=None, top_level=False, is_last_item=None, references=None):
    references = references or {}
    if id(object_) in references:
        # if the address is known, substitute its repr with reference name
        name = references[id(object_)]

        # add it also to dependencies
        requirement = ("." + sub_module_name(name), name)
        if requirement not in dep_list:
            dep_list.append(requirement)
        yield name

    elif hasattr(object_, "make_py_reference"):
        for element in object_.dispatch_repr(dep_list, references=references):
            yield element

    elif isinstance(object_, list):
        items_reprs = [(None, list(dispatch_repr(item, dep_list, is_last_item=is_last, references=references)))
                       for item, is_last in mark_last(object_)]
        for element in make_a_markup(u"[", items_reprs, u"]"):
            yield element
    elif isinstance(object_, tuple):
        items_reprs = [(None, list(dispatch_repr(item, dep_list, is_last_item=is_last, references=references)))
                       for item, is_last in mark_last(object_)]
        for element in make_a_markup(u"(", items_reprs, u",)" if len(object_) == 1 else u")"):
            yield element
    elif isinstance(object_, set):
        items_reprs = [(None, list(dispatch_repr(item, dep_list, is_last_item=is_last, references=references)))
                       for item, is_last in mark_last(sorted(object_))]
        if not items_reprs:
            yield u"set()"
        else:
            for element in make_a_markup(u"{", items_reprs, u"}"):
                yield element
    elif isinstance(object_, OrderedDict):
        if dep_list is not None:
            dep_list.append((u"collections", u"OrderedDict"))
        items_reprs = [(None, list(dispatch_repr(item, dep_list, is_last_item=is_last, references=references)))
                       for item, is_last in mark_last(object_.items())]
        for element in make_a_markup(u"OrderedDict([", items_reprs, u"])"):
            yield element

    elif isinstance(object_, dict):
        items_reprs = [(kw, list(dispatch_repr(value, dep_list, is_last_item=is_last, references=references)))
                       for (kw, value), is_last in mark_last(sorted(object_.items(), key=lambda x: str(x[0])))]
        for element in make_a_markup(u"{", items_reprs, u"}", as_dict=True):
            yield element

    elif isinstance(object_, six.string_types) and len(object_) > 80:
        if top_level:
            yield u"(\n"
            indent = u"    "
        else:
            indent = u""
        for line, is_last_part in mark_last(list(_split_long_string(object_))):
            yield indent + repr(line) + (u"\n" if not is_last_part or is_last_item else u",\n")
        if top_level:
            yield u")"

    else:
        try:
            yield repr(object_)
        except Exception:
            yield object.__repr__(object_)


def mark_last(iterable):
    num_elements = len(iterable)
    for number, item in enumerate(iterable, 1):
        is_last = number == num_elements
        yield item, is_last


def sub_module_name(plain_variable_name):
    return "_sub_" + plain_variable_name


def make_a_markup(begin, items_reprs, end, item_delimiter=u",", as_dict=False):
    single_line_body = u", ".join(_form_single_line(items_reprs, as_dict))
    single_line_reproduction = begin + single_line_body + end
    if len(single_line_reproduction) <= 100 or not items_reprs:
        yield single_line_reproduction
    else:
        yield begin + u"\n"
        for element in _form_multi_line(items_reprs, item_delimiter, as_dict):
            yield element
        yield end


def _do_interfere(ordered_name_value_pairs, kw_pairs):
    kw_pairs = kw_pairs or {}
    ordered_name_value_pairs = list(ordered_name_value_pairs) + sorted(kw_pairs.items())
    validate_objects(ordered_name_value_pairs)
    return ordered_name_value_pairs


def validate_objects(objects):
    for i, item in enumerate(objects):
        if not isinstance(item, tuple):
            msg = u"Expecting item number {} to be tuple, got {}."
            raise TypeError(msg.format(i, type(item).__name__))
        if len(item) != 2:
            raise TypeError(u"Expecting tuples with two items, got {} at item number {}".format(len(item), i))
        name, obj = item
        if not isinstance(name, six.string_types):
            msg = u"Expecting first item in tuple to be a string, got {} at item number {}"
            raise TypeError(msg.format(type(name).__name__, i))
        if not PY_IDENTIFIER_VALIDATOR.match(name):
            raise ValueError(u"{} is not a valid python identifier - given at item number {}".format(name, i))


def _form_single_line(items_representations, as_dict):
    kw_delimiter = u": " if as_dict else u"="
    for keyword, value_reps in items_representations:
        if keyword:
            if as_dict:
                keyword = repr(keyword)
            preamble = keyword + kw_delimiter
        else:
            preamble = u""
        yield preamble + u"".join(value_reps)


def _form_multi_line(items_reprs, item_delimiter, as_dict):
    kw_delimiter = u": " if as_dict else u"="
    indent = u"    "
    for keyword, value_reps in items_reprs:
        is_first = True
        for argument_reproduction in value_reps:
            if is_first and keyword is not None:
                if as_dict:
                    keyword = repr(keyword)
                preamble = keyword + kw_delimiter
            else:
                preamble = u""
            optional_break = (item_delimiter + u"\n") if not argument_reproduction.endswith(u"\n") else u""
            is_first = False
            yield indent + preamble + argument_reproduction + optional_break


def _split_long_string(long_string, max_line_width=80):
    lines = long_string.split(u"\n")
    if not any(len(line) > max_line_width for line in lines):
        for not_last, line in enumerate(lines, 1 - len(lines)):
            yield line + (u"\n" if not_last else u"")
    else:
        words = long_string.split(u" ")
        if not any(len(word) > max_line_width for word in words):
            line, pos = u"", 0
            for not_last, word in enumerate(words, 1 - len(words)):
                word += u" " if not_last else u""
                line += word
                pos += len(word)
                if pos >= 80:
                    yield line
                    line, pos = u"", 0
            if line:
                yield line
        else:
            pos = 0
            while pos < len(long_string):
                yield long_string[pos:pos + max_line_width]
                pos += max_line_width
