""" Auto keyref ajax functions
"""
import json

from django.http.response import HttpResponse

from core_module_auto_key_app.components.auto_key import api as auto_key_api
from core_module_auto_keyref_app.components.auto_keyref import api as auto_keyref_api
from core_parser_app.components.data_structure_element import api as data_structure_element_api
from core_parser_app.tools.modules.exceptions import ModuleError


def get_updated_keys(request):
    """ Return current keys

        updated_keys[key] = {'ids': [],
                            'tagIDs': []}
        key = key name
        ids = list of possible values for a key
        tagIDs = HTML element that needs to be updated with the values (keyrefs)

    Args:
        request:

    Returns:

    """
    try:
        # get root id
        root_id = request.GET['root_id']
        # get root element from id
        root_element = data_structure_element_api.get_by_id(root_id)

        # get auto key manager from root
        auto_key = auto_key_api.get_by_root(root_element)

        # go through all existing keys
        for key, module_ids in auto_key.keys.iteritems():
            # get list of current module ids
            current_module_ids = _get_current_module_ids(module_ids)
            # update list of module ids in auto key manager
            auto_key.keys[key] = current_module_ids

        # update auto key manager
        auto_key_api.upsert(auto_key)

        # get auto keyref manager from root
        auto_keyref = auto_keyref_api.get_by_root(root_element)

        # go through all existing keyrefs
        for keyref, module_ids in auto_keyref.keyrefs.iteritems():
            # get list of current module ids
            current_module_ids = _get_current_module_ids(module_ids)
            # update list of module ids in auto keyref manager
            auto_keyref.keyrefs[keyref] = current_module_ids

        # update auto keyref manager
        auto_keyref_api.upsert(auto_keyref)

        # get the list of keyrefs to update
        updated_keyrefs = []
        for keyref, module_ids in auto_keyref.keyrefs.iteritems():
            updated_keyrefs.extend(module_ids)
    except Exception, e:
        raise ModuleError("An unexpected error occurred while getting updated list of keys: " + e.message)

    return HttpResponse(json.dumps(updated_keyrefs), content_type='application/javascript')


def _get_current_module_ids(module_ids):
    """ Return list of module ids still present in the data structure

    Args:
        module_ids:

    Returns:

    """
    # Initialize list of current module ids
    current_module_ids = []
    # go through all module ids
    for module_id in module_ids:
        try:
            # try to get element
            data_structure_element_api.get_by_id(module_id)
            # add id to list if element still exists
            current_module_ids.append(module_id)
        except Exception:
            pass
    return current_module_ids
