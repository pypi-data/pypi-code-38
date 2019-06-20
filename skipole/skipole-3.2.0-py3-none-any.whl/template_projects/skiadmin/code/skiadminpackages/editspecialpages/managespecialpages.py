

import re
# a search for anything none-alphanumeric and not an underscore
_AN = re.compile('[^\w_]')


from skipole import skilift
from .. import utils

from skipole import FailPage, ValidateError, ServerError


def retrieve_managepage(skicall):
    "this call is for the manage special pages page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # clears any session data
    utils.clear_call_data(call_data)

    project = call_data['editedprojname']
    labeldict = skilift.labels(project)

    page_data[("adminhead","page_head","large_text")] = "Manage page labels"

    system_list = skilift.sys_list()
    page_data['system:col_label'] = system_list
    page_data['system:col_input'] = _make_list(project, system_list, labeldict)
    page_data['system:hidden_field1'] = system_list

    lib_list = skilift.lib_list()
    page_data['jq:col_label'] = lib_list
    page_data['jq:col_input'] = _make_list(project, lib_list, labeldict)
    page_data['jq:hidden_field1'] = lib_list

    user_label_list = [item for item in labeldict if ( (item not in system_list) and (item not in lib_list) )]
    if user_label_list:
        user_label_list.sort()
        page_data['user:col_label'] = user_label_list
        page_data['user:col_input'] = _make_list(project, user_label_list, labeldict)
        page_data['user:hidden_field1'] = user_label_list
    else:
        page_data['user:show'] = False



def _make_list(project, reflist, labeldict):
    "Creates a list of url's or string ident numbers of items in reflist"
    result = []
    for item in reflist:
        if item in labeldict:
            target = labeldict[item]
            if isinstance(target, str):
                # its a url
                result.append(target)
            else:
                # its a tuple
                if target[0] == project:
                    result.append(str(target[1]))
                else:
                    result.append(",".join(target))
        else:
            result.append('')
    return result


def submit_special_page(skicall):
    "Sets special page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    label = call_data["label"]
    ident_or_url = call_data["ident_or_url"]
    if (not label) or (not ident_or_url):
        raise FailPage(message = "label or ident missing")

    # check label is valid
    if _AN.search(label):
        raise FailPage(message = "The label can only contain A-Z, a-z, 0-9 and the underscore character.")

    if '_' in label:
        labelparts = label.split('_')
        for lpart in labelparts:
            if lpart.isdigit():
                raise FailPage(message = "Invalid label (Danger of confusion with a page ident, please avoid using digits without letters).")

    if label.isdigit():
        raise FailPage(message = "Invalid label (Danger of confusion with a page ident).")

    try:
        skilift.set_label(project, label, ident_or_url)
    except ServerError as e:
        raise FailPage(message = e.message)

    if label in skilift.sys_list():
        call_data['status'] = 'System special page %s set' % (label,)
        return
    if label in skilift.lib_list():
        call_data['status'] = 'Library special page %s set' % (label,)
        return
    call_data['status'] = 'Label %s set' % (label,)


def add_user_page(skicall):
    "Sets user defined label and target"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    label = call_data["label"]
    ident_or_url = call_data["ident_or_url"]
    if (not label) or (not ident_or_url):
        raise FailPage(message = "label or ident missing", widget='addlabel')

    # check label is valid
    if _AN.search(label):
        raise FailPage(message = "The label can only contain A-Z, a-z, 0-9 and the underscore character.")

    if '_' in label:
        labelparts = label.split('_')
        for lpart in labelparts:
            if lpart.isdigit():
                raise FailPage(message = "Invalid label (Danger of confusion with a page ident, please avoid using digits without letters).")

    if label.isdigit():
        raise FailPage(message = "Invalid label (Danger of confusion with a page ident).")

    if label in skilift.lib_list():
        raise FailPage(message = "Invalid label, reserved for system files.")
    if label in skilift.sys_list():
        raise FailPage(message = "Invalid label, reserved for system pages.")

    try:
        skilift.set_label(project, label, ident_or_url)
    except ServerError as e:
        raise FailPage(message = e.message)
    call_data['status'] = 'Label %s set' % (label,)


def submit_user_page(skicall):
    "Edits or deletes a special user page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    if 'label' not in call_data:
        raise FailPage(message = "Invalid label.")
    label = call_data["label"]
    if label in skilift.lib_list():
        raise FailPage(message = "Invalid label.")
    if label in skilift.sys_list():
        raise FailPage(message = "Invalid label.")
    if ("edit" in call_data) and (call_data["edit"]):
        submit_special_page(skicall)
        return
    if ("delete" not in call_data) or (not call_data["delete"]):
        raise FailPage(message = "Invalid submission.")
    try:
        skilift.delete_label(project, label)
    except ServerError as e:
        raise FailPage(message = e.message)
    call_data['status'] = 'User label deleted'


