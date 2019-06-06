# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from .._exceptions import DefinitionError
from .._text import enumeration, plural
from .._utils.parse import find_variables


class Definition:
    DICT_ATTRS = None

    def as_dict(self):
        return {k: getattr(self, k) for k in self.DICT_ATTRS}

    def __eq__(self, other):
        if isinstance(other, dict):
            return self.as_dict() == other
        elif isinstance(other, Definition):
            return self.as_dict() == other.as_dict()
        else:
            return False


def name_ok(key: str, allow_empty: bool) -> bool:
    if not key and not allow_empty:
        return False
    try:
        return all(c not in key for c in ' ')
    except TypeError:
        return False


def check_names(keys, attribute, allow_empty: bool):
    invalid = [key for key in keys if not name_ok(key, allow_empty)]
    if invalid:
        raise DefinitionError(f"Invalid {plural('name', len(invalid))} for {attribute}: {enumeration(invalid)}")


def compound(items):
    out = ''
    for item in items:
        if item == '*':
            if not out.endswith('*'):
                out += '*'
        elif item:
            if out and not out.endswith('*'):
                out += ' '
            out += item
    return out


def dict_change(old, new):
    "Readable representation of dict change"
    lines = []
    keys = set(new)
    keys.update(old)
    for key in sorted(keys):
        if key not in new:
            lines.append("%r: %r -> key removed" % (key, old[key]))
        elif key not in old:
            lines.append("%r: new key -> %r" % (key, new[key]))
        elif new[key] != old[key]:
            lines.append("%r: %r -> %r" % (key, old[key], new[key]))
    return lines


def log_dict_change(log, kind, name, old, new):
    log.warning("  %s %s changed:", kind, name)
    for line in dict_change(old, new):
        log.warning("    %s", line)


def log_list_change(log, kind, name, old, new):
    log.warning("  %s %s changed:", kind, name)
    removed = tuple(v for v in old if v not in new)
    if removed:
        log.warning("    Members removed: %s", ', '.join(map(str, removed)))
    added = tuple(v for v in new if v not in old)
    if added:
        log.warning("    Members added: %s", ', '.join(map(str, added)))


def find_epoch_vars(params):
    "Find variables used in a primary epoch definition"
    out = set()
    if params.get('sel'):
        out.update(find_variables(params['sel']))
    if 'trigger_shift' in params and isinstance(params['trigger_shift'], str):
        out.add(params['trigger_shift'])
    if 'post_baseline_trigger_shift' in params:
        out.add(params['post_baseline_trigger_shift'])
    return out


def find_epochs_vars(epochs):
    "Find variables used in all epochs"
    todo = list(epochs)
    out = {}
    while todo:
        for e in tuple(todo):
            p = epochs[e]
            if 'sel_epoch' in p:
                if p['sel_epoch'] in out:
                    out[e] = find_epoch_vars(p)
                    out[e].update(out[p['sel_epoch']])
                    todo.remove(e)
            elif 'sub_epochs' in p:
                if all(se in out for se in p['sub_epochs']):
                    out[e] = find_epoch_vars(p)
                    for se in p['sub_epochs']:
                        out[e].update(out[se])
                    todo.remove(e)
            elif 'collect' in p:
                if all(se in out for se in p['collect']):
                    out[e] = find_epoch_vars(p)
                    for se in p['collect']:
                        out[e].update(out[se])
                    todo.remove(e)
            else:
                out[e] = find_epoch_vars(p)
                todo.remove(e)
    return out


def find_dependent_epochs(epoch, epochs):
    "Find all epochs whose definition depends on epoch"
    todo = set(epochs).difference(epoch)
    out = [epoch]
    while todo:
        last_len = len(todo)
        for e in tuple(todo):
            p = epochs[e]
            if 'sel_epoch' in p:
                if p['sel_epoch'] in out:
                    out.append(e)
                    todo.remove(e)
            elif 'sub_epochs' in p:
                if any(se in out for se in p['sub_epochs']):
                    out.append(e)
                    todo.remove(e)
            elif 'collect' in p:
                if any(se in out for se in p['collect']):
                    out.append(e)
                    todo.remove(e)
            else:
                todo.remove(e)
        if len(todo) == last_len:
            break
    return out[1:]


def typed_arg(arg, type_):
    return None if arg is None else type_(arg)
