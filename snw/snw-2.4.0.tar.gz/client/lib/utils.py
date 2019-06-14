import os
import json

import requests

_reqcache = {}


def getcache(url, auth, params):
    global _reqcache
    key = json.dumps([url, params])
    if key not in _reqcache:
        _reqcache[key] = requests.get(url, auth=auth, params=params)
    return _reqcache[key]


def entity_list(url, auth):
    r = getcache(os.path.join(url, "entity/list"),
                 auth=auth, params={"detail": True})
    return r.status_code, r.json()


def get_entity(url, auth, code):
    try:
        code_id = int(code)
        return True, code_id
    except Exception:
        pass
    status_code, entities = entity_list(url, auth)
    if status_code != 200:
        return False, "cannot get entity list"
    for e in entities:
        if e["entity_code"] == code or e["name"] == code:
            return True, e["id"]
    return False, "unknown entity"


def group_list(url, auth):
    r = getcache(os.path.join(url, "group/list"),
                 auth=auth, params={"detail": True})
    return r.status_code, r.json()


def get_group(url, auth, code):
    try:
        code_id = int(code)
        return True, code_id
    except Exception:
        pass
    codesplit = code.split(':')
    entity_id = None
    if len(codesplit) == 2:
        status_code, entity_id = get_entity(url, auth, codesplit[0])
        code = codesplit[1]
        if not status_code:
            return False, entity_id
    elif len(codesplit) > 2:
            return False, "invalid code"

    status_code, codes = group_list(url, auth)
    if status_code != 200:
        return False, "cannot get group list"
    for c in codes:
        if c.get("entity_id") == entity_id and c["name"] == code:
            return True, c["id"]
    return False, "unknown group"


def role_list(url, auth):
    r = getcache(os.path.join(url, "role/list"),
                 auth=auth, params={"detail": True})
    return r.status_code, r.json()


def get_role(url, auth, code):
    try:
        code_id = int(code)
        return True, code_id
    except Exception:
        pass
    codesplit = code.split(':')
    entity_id = None
    if len(codesplit) == 2:
        status_code, entity_id = get_entity(url, auth, codesplit[0])
        code = codesplit[1]
        if not status_code:
            return False, entity_id
    elif len(codesplit) > 2:
            return False, "invalid code"

    status_code, codes = role_list(url, auth)
    if status_code != 200:
        return False, "cannot get role list"
    for c in codes:
        if c.get("entity_id") == entity_id and c["name"] == code:
            return True, c["id"]
    return False, "unknown role"


def user_list(url, auth):
    r = getcache(os.path.join(url, "user/list"),
                 auth=auth, params={"detail": True})
    return r.status_code, r.json()


def get_user(url, auth, user):
    try:
        user_id = int(user)
        return True, user_id
    except Exception:
        pass

    status_code, users = user_list(url, auth)
    if status_code != 200:
        return False, "cannot get user list"
    for u in users:
        # warning: .lower() works for email but not for some special characters
        # https://stackoverflow.com/questions/319426/how-do-i-do-a-case-insensitive-string-comparison
        if u["email"].lower() == user.lower() or u["tid"].lower() == user.lower():
            return True, u["id"]
    return False, "unknown user"


def permission_list(url, auth):
    r = getcache(os.path.join(url, "permission/list"),
                 auth=auth, params={"detail": True})
    return r.status_code, r.json()


def get_permission(url, auth, permission):
    try:
        permission_id = int(permission)
        return True, permission_id
    except Exception:
        pass

    status_code, permissions = permission_list(url, auth)
    if status_code != 200:
        return False, "cannot get permission list"
    for p in permissions:
        if p["name"] == permission:
            return True, p["id"]
    return False, "unknown permission"
