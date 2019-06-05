import uforgecli_utils
from ussclicore.utils.printer import *

def org_get(api, name, on_error_raise = True):
    try:
        org = None
        if name is None:
            org = api.Orgs("default").Get()
            return org
        else:
            orgs = api.Orgs().Getall(None)
            for o in orgs.orgs.org:
                if o.name == name:
                    org = o
    except Exception as e:
        uforgecli_utils.print_uforge_exception(e)

    if org is None and on_error_raise:
        raise Exception ("Unable to find organization")
    return org