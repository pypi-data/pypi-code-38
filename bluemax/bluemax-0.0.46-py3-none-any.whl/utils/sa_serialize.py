from sqlalchemy.orm import class_mapper, ColumnProperty
from sqlalchemy.orm.session import object_session
from collections import OrderedDict
import logging


def dumps(item):
    result = {"_type_": item.__class__.__name__}
    for prop in class_mapper(item.__class__).iterate_properties:
        if prop.key[0] == "_":
            continue
        if isinstance(prop, ColumnProperty):
            result[prop.key] = getattr(item, prop.key)
    return result


def loads(values, item):
    for prop in class_mapper(item.__class__).iterate_properties:
        if prop.key[0] == "_":
            continue
        if isinstance(prop, ColumnProperty) and prop.key in values.keys():
            setattr(item, prop.key, values.get(prop.key))


def from_pairs(o, obj):
    for key in o.__mapper__.c.keys():
        if key[0] == "_" or key in ["id", "last_updated"]:
            continue
        value = obj.get(key)
        logging.debug("set %s:%r", key, value)
        if key == "version_id" and value == None:
            continue
        setattr(o, key, value)


def from_one_to_many_pairs(o, pairs, key, clazz):
    """Simple saving of one-to-many relations - not usually associated with from_pairs"""
    added = []
    updated = []
    deleted = []
    errors = []
    session = object_session(o)
    existing_keys = [i.id for i in getattr(o, key)]
    for item in pairs.get(key, []):
        item_id = item.get("id")
        obj = None
        if item_id:
            if int(item_id) < 0:
                obj = session.query(clazz).get(abs(int(item_id)))
                session.delete(obj)
                deleted.append(obj)
                continue
            else:
                if item_id in existing_keys:
                    existing_keys.remove(item_id)
                obj = session.query(clazz).get(item_id)
                if from_pairs(obj, item) is True:
                    e = obj._validate_()
                    if e:
                        errors.extend(e)
                    updated.append(obj)
        else:
            obj = clazz()
            getattr(o, key).append(obj)
            if from_pairs(obj, item) is True:
                e = obj._validate_()
                if e:
                    errors.extend(e)
                added.append(obj)
    for key in existing_keys:
        obj = session.query(clazz).get(abs(int(key)))
        session.delete(obj)
        deleted.append(obj)
    return added, updated, deleted, errors


def from_many_to_many_pairs(o, pairs, key, clazz):
    """Simple saving of many-to-many relations - not usually associated with from_pairs"""
    added = []
    removed = []
    session = object_session(o)
    existing = dict([(a.id, a) for a in getattr(o, key)])
    new_list = dict([(b.get("id"), b) for b in pairs.get(key, [])])
    for to_remove in set(existing.keys()) - set(new_list.keys()):
        obj = existing[to_remove]
        getattr(o, key).remove(obj)
        removed.append(obj)
        logging.info("m2m removed %s", obj)
    for to_add in set(new_list.keys()) - set(existing.keys()):
        obj = session.query(clazz).get(abs(int(to_add)))
        getattr(o, key).append(obj)
        added.append(obj)
        logging.info("m2m added %s", obj)
    return added, removed
