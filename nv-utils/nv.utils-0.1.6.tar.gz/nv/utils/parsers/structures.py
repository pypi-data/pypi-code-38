from collections.abc import Sequence, Set, Mapping

from .string import parse_str


__all__ = ["parse_structure"]


def _check(obj):
    return bool(obj) if (isinstance(obj, (Sequence, Set, Mapping)) or obj is None) else True


def _apply_subparser(obj, subparser, clean_up):
    output = subparser(obj, clean_up)
    check = _check(output) if clean_up else True
    return output, check


def _parse_seq(seq, subparser, clean_up):
    return [r for r, check in (_apply_subparser(i, subparser, clean_up) for i in seq) if check]


def _parse_set(s, subparser, clean_up):
    return {r for r, check in (_apply_subparser(i, subparser, clean_up) for i in s) if check}


def _parse_map(m, subparser, clean_up):
    return {k: r[0] for k, r in ((k, _apply_subparser(v, subparser, clean_up)) for k, v in m.items()) if r[1]}


def parse_structure(struct, str_parser=parse_str, default_parser=None, clean_up=False):

    def parser(obj, _clean_up):
        if isinstance(obj, str):
            output = str_parser(obj)
        elif isinstance(obj, Sequence):
            output = _parse_seq(obj, parser, _clean_up)
        elif isinstance(obj, Set):
            output = _parse_set(obj, parser, _clean_up)
        elif isinstance(obj, Mapping):
            output = _parse_map(obj, parser, _clean_up)
        else:
            output = default_parser(obj) if default_parser else obj
        return output

    return parser(struct, clean_up)
