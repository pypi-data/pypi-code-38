#!/usr/bin/env python
from functools import reduce, singledispatch
import collections
import json
import xmltodict

OrderedDict = collections.OrderedDict


def handle_leaf(parent_path: str, path: str, tag: str, attributes: dict, value: str):
    return {
        "parent_path": parent_path,
        "path": path,
        "tag": tag,
        "attributes": attributes,
        "value": value,
    }


def handle_dict(parent_path: str, path: str, tag: str, value: OrderedDict):
    assert isinstance(value, (dict, OrderedDict))

    yield handle_leaf(
        parent_path=parent_path,
        path=path,
        tag=tag,
        attributes={k[1:]: v for k, v in value.items() if k.startswith("@")},
        value=value.get("#text", {}),
    )
    yield from walk_tree(value, path)


def handle_list(parent_path: str, path: str, tag: str, value: list):
    assert isinstance(value, list)
    for e in value:
        assert e is None or isinstance(e, (str, dict, OrderedDict))

    for i, e in enumerate(value):
        if isinstance(e, (OrderedDict, dict)):
            _attributes = {k[1:]: v for k, v in e.items() if k.startswith("@")}
            _value = e.get("#text", {})
        elif isinstance(e, str):
            _attributes = {}
            _value = e
        elif e is None:
            _attributes = {}
            _value = ""
        else:
            raise TypeError("found unexpected type")

        yield handle_leaf(
            parent_path=parent_path,
            path="%s%s/" % (path, i),
            tag=tag,
            attributes=_attributes,
            value=_value,
        )

        if isinstance(e, (OrderedDict, dict)):
            yield from walk_tree(e, "%s%s/" % (path, i))


def walk_tree(t, path="/"):
    assert isinstance(t, (dict, OrderedDict))
    for key, value in t.items():
        if key.startswith("@") or key == "#text":  # skip attributes and leaf contents
            continue
        if value is None:  # contents of empty leaf elements, ie <a></a>
            value = ""

        if isinstance(value, (dict, OrderedDict)):
            yield from handle_dict(
                parent_path=path, path="%s%s/" % (path, key), tag=key, value=value
            )

        elif isinstance(value, list):
            yield from handle_list(
                parent_path=path, path="%s%s/" % (path, key), tag=key, value=value
            )

        elif isinstance(value, (str, int)):
            yield handle_leaf(
                parent_path=path,
                path="%s%s/" % (path, key),
                tag=key,
                attributes={},
                value=value,
            )

        else:
            import pdb

            pdb.set_trace()
            raise TypeError("found unexpected type")


def merge_tagvalue_into_row(row, tag, val):
    "Merges a tag:value into a row."
    assert isinstance(row, dict), "Row is not a dict?"
    if tag not in row["value"]:  # it doesn't have our tag yet.
        row["value"][tag] = val
    else:  # It has our tag...
        if isinstance(row["value"][tag], list):  # its a list
            row["value"][tag] = [*row["value"][tag], val]  # append to current list
        else:  # it is not a list, so make it one.
            row["value"][tag] = [row["value"][tag], val]
    return row


def combine_two_rows(cur_row, next_row):
    "Merges the next row's value & attributes into the current row."
    tag = next_row["tag"]
    val = next_row["value"]
    attrib = next_row["attributes"]
    cur_row = merge_tagvalue_into_row(cur_row, tag, val)
    for k, aval in attrib.items():
        atag = "@%s.%s" % (tag, k)
        cur_row = merge_tagvalue_into_row(cur_row, atag, aval)
    return cur_row


def parse_reducer(rows, next_row):
    assert isinstance(rows, (list, type(None))), "rows must be list or none?"
    if not rows:  # so it begins
        return [next_row]  # put it in a list and start.
    if next_row["value"] == {}:  # start over, we found a new row.
        return [*rows, next_row]
    else:  # This is the actual rollup.
        *head, tail = rows
        if not isinstance(tail["value"], (dict, list)):
            # TODO This is the gross nested tag in text that tucker found.
            tail["value"] = {"#text": tail["value"]}
            return [*head, tail, next_row]
        tail = combine_two_rows(tail, next_row)
        return [*head, tail]


def is_maybe_xml(s: str):
    """ (gently) tests if the file is xml by evaluating the first non-whitespace character.
    This is used for disptach to xmltodict and/or json.loads, which in turn will
    throw errors on data which is not well-formed.

    TODO would be great to do this with http content negotiation?"""
    if not isinstance(s, str):
        return False
    if s.lstrip()[0] == "<":
        return True
    else:
        return False


@singledispatch
def parse(data):
    import pdb

    return data


@parse.register(str)
def _(data: str):
    if is_maybe_xml(data):
        # TODO do i need force_cdata?
        # dict_data = xmltodict.parse(data, force_cdata=True)
        dict_data = xmltodict.parse(data)
    else:
        dict_data = json.loads(data, object_hook=OrderedDict)

    intermediate = walk_tree(dict_data)
    return list(reduce(parse_reducer, intermediate, None))


@parse.register(OrderedDict)
@parse.register(dict)
def _(data: dict):
    # intermediate should already be done; they probably already did xmltodict.parse somehow.
    intermediate = walk_tree(data)
    return list(reduce(parse_reducer, intermediate, None))
