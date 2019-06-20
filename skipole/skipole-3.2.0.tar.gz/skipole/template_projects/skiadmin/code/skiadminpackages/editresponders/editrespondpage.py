

"Functions implementing respond page editing"

import collections


from skipole import skilift
from skipole.skilift import editresponder

from skipole import ValidateError, FailPage, ServerError, GoTo

from .. import utils

def _ident_to_str(ident):
    "Returns string ident or label"
    if ident is None:
        return ''
    if isinstance(ident, str):
        return ident
    # ident must be a list or tuple of (project,number)
    if len(ident) != 2:
        raise FailPage("Invalid ident")
    return ident[0] + "," + str(ident[1])


def _field_to_string(wfield):
    "Returns two forms of a widgfield, or if a string, then just the string twice"
    if isinstance(wfield, str):
        return wfield, wfield
    # a widgfield has four elements, reduce it to the non empty elements
    shortwfield = [ w for w in wfield if w ]
    if len(shortwfield) == 1:
        return shortwfield[0], shortwfield[0]
    wf1 = ",".join(shortwfield)
    if len(shortwfield) == 2:
        wf2 = shortwfield[0] + ":" + shortwfield[1]
    else:
        wf2 = shortwfield[0] + "-" + shortwfield[1] + ":" + shortwfield[2]
    return wf1, wf2


def _t_ref(r_info, item):
    "Returns a TextBlock ref for the given item"
    return ".".join(["responders", r_info.module_name, r_info.responder, item])



def skicall_help(skicall):
    "Retrieves help text for the skicall object"
    text = skicall.textblock("aboutcode.skicall")
    if not text:
        text = "No help text for aboutcode.skicall has been found"
    skicall.page_data[("adminhead","show_help","para_text")] = "\n" + text
    skicall.page_data[("adminhead","show_help","hide")] = False


def use_submit_list_help(skicall):
    "Retrieves help text for the use_submit_list decorator"
    text = skicall.textblock("aboutcode.usesubmitlist")
    if not text:
        text = "No help text for aboutcode.use_submit_list has been found"
    skicall.page_data[("adminhead","show_help","para_text")] = "\n" + text
    skicall.page_data[("adminhead","show_help","hide")] = False


def fail_page_help(skicall):
    "Retrieves help text for the fail page ident"
    text = skicall.textblock("responders.fail_page")
    if not text:
        text = "No help text for responders.fail_page has been found"
    skicall.page_data[("adminhead","show_help","para_text")] = "\n" + text
    skicall.page_data[("adminhead","show_help","hide")] = False


def submit_data_help(skicall):
    "Retrieves help text for the submit_data function"
    call_data = skicall.call_data
    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
    else:
        raise FailPage(message = "page missing")
    try:
        project = call_data['editedprojname']
        # get a ResponderInfo named tuple with information about the responder
        r_info = editresponder.responder_info(project, pagenumber, call_data['pchange'])
    except ServerError as e:
        raise FailPage(message=e.message)
    sdtextref = _t_ref(r_info, 'submit_data')
    text = skicall.textblock(sdtextref)
    if not text:
        text = "No help text for %s has been found" % sdtextref
    skicall.page_data[("adminhead","show_help","para_text")] = "\n" + text
    skicall.page_data[("adminhead","show_help","hide")] = False


def submit_dict_help(skicall):
    "Retrieves help text for the responder submit_dict"
    call_data = skicall.call_data
    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
    else:
        raise FailPage(message = "page missing")
    try:
        project = call_data['editedprojname']
        # get a ResponderInfo named tuple with information about the responder
        r_info = editresponder.responder_info(project, pagenumber, call_data['pchange'])
    except ServerError as e:
        raise FailPage(message=e.message)
    sdtextref = _t_ref(r_info, 'submit_dict')
    text = skicall.textblock(sdtextref)
    if not text:
        text = "No help text for %s has been found" % sdtextref
    skicall.page_data[("adminhead","show_help","para_text")] = "\n" + text
    skicall.page_data[("adminhead","show_help","hide")] = False


def call_data_help(skicall):
    "Retrieves help text for the responder call_data"
    call_data = skicall.call_data
    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
    else:
        raise FailPage(message = "page missing")
    try:
        project = call_data['editedprojname']
        # get a ResponderInfo named tuple with information about the responder
        r_info = editresponder.responder_info(project, pagenumber, call_data['pchange'])
    except ServerError as e:
        raise FailPage(message=e.message)
    cdtextref = _t_ref(r_info, 'call_data')
    text = skicall.textblock(cdtextref)
    if not text:
        text = "No help text for %s has been found" % cdtextref
    skicall.page_data[("adminhead","show_help","para_text")] = "\n" + text
    skicall.page_data[("adminhead","show_help","hide")] = False


def retrieve_edit_respondpage(skicall):
    "Retrieves widget data for the edit respond page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # clears any session data, keeping page_number, pchange and any status message
    utils.clear_call_data(call_data, keep=["page_number", "pchange", "status"])

    if 'page_number' in call_data:
        pagenumber = call_data['page_number']
        str_pagenumber = str(pagenumber)
    else:
        raise FailPage(message = "page missing")

    try:
        project = call_data['editedprojname']
        pageinfo = skilift.page_info(project, pagenumber)

        if pageinfo.item_type != 'RespondPage':
            raise FailPage(message = "Invalid page")

        call_data['pchange'] = pageinfo.change

        # fills in the data for editing page name, brief, parent, etc., 
        page_data[("adminhead","page_head","large_text")] = pageinfo.name
        page_data[('page_edit','p_ident','page_ident')] = (project,str_pagenumber)
        page_data[('page_edit','p_name','page_ident')] = (project,str_pagenumber)
        page_data[('page_edit','p_description','page_ident')] = (project,str_pagenumber)
        page_data[('page_edit','p_rename','input_text')] = pageinfo.name
        page_data[('page_edit','p_parent','input_text')] = "%s,%s" % (project, pageinfo.parentfolder_number)
        page_data[('page_edit','p_brief','input_text')] = pageinfo.brief

        # get a ResponderInfo named tuple with information about the responder
        r_info = editresponder.responder_info(project, pagenumber, call_data['pchange'])
    except ServerError as e:
        raise FailPage(message=e.message)

    page_data['respondertype:para_text'] = "This page is a responder of type: %s." % (r_info.responder,)
    page_data['responderdescription:textblock_ref'] = ".".join(["responders",r_info.module_name, r_info.responder])

    if r_info.widgfield_required:
        if r_info.widgfield:
            page_data['widgfield:input_text'] = r_info.widgfield
    else:
        page_data['widgfield:show'] = False

    if r_info.alternate_ident_required:
        page_data['alternate','input_text'] = _ident_to_str(r_info.alternate_ident)
        page_data['alternate_ident_description','textblock_ref'] = _t_ref(r_info, 'alternate_ident')
    else:
        page_data['alternate','show'] = False
        page_data['alternate_ident_description','show'] = False

    if r_info.target_ident_required:
        page_data['target:input_text'] = _ident_to_str(r_info.target_ident)
        page_data['target_ident_description','textblock_ref'] = _t_ref(r_info, 'target_ident')
    else:
        page_data['target:show'] = False
        page_data['target_ident_description','show'] = False

    if r_info.allowed_callers_required:
        page_data['allowed_callers_description:textblock_ref'] = _t_ref(r_info, 'allowed_callers')
        if r_info.allowed_callers:
            contents = []
            for ident in r_info.allowed_callers:
                ident_row = [_ident_to_str(ident), _ident_to_str(ident).replace(",","_")]
                contents.append(ident_row)
            page_data['allowed_callers_list:contents'] = contents
        else:
            page_data['allowed_callers_list:show'] = False
        page_data['add_allowed_caller:input_text'] = ''
    else:
        page_data['allowed_callers_description:show'] = False
        page_data['allowed_callers_list:show'] = False
        page_data['add_allowed_caller:show'] = False

    # validate option
    if r_info.validate_option_available:
        page_data[('val_option_desc', 'textblock_ref')] =  _t_ref(r_info, 'validate_option')
        if r_info.validate_option:
            page_data['set_val_option','button_text'] = "Disable Validation"
            page_data['val_status','para_text'] = "Validate received field values : Enabled"
            page_data['validate_fail', 'input_text'] = _ident_to_str(r_info.validate_fail_ident)
            page_data['validate_fail', 'hide'] = False
        else:
            page_data['set_val_option','button_text'] = "Enable Validation"
            page_data['val_status','para_text'] = "Validate received field values : Disabled"
            page_data['validate_fail', 'hide'] = True
    else:
        page_data['val_option_desc','show'] = False
        page_data['set_val_option','show'] = False
        page_data['val_status','show'] = False
        page_data['validate_fail', 'show'] = False

    
    # submit option

    if r_info.submit_option_available:
        page_data['submit_option_desc','textblock_ref'] = _t_ref(r_info, 'submit_option')
        if r_info.submit_option:
            page_data['set_submit_option','button_text'] = 'Disable submit_data'
            page_data['submit_status','para_text'] = "Call submit_data : Enabled"
        else:
            page_data['set_submit_option','button_text'] = 'Enable submit_data'
            page_data['submit_status','para_text'] = "Call submit_data : Disabled"
    else:
        page_data['submit_option_desc','show'] = False
        page_data['set_submit_option','show'] = False
        page_data['submit_status','show'] = False

    if r_info.submit_required or r_info.submit_option:
        page_data['submit_list_description','textblock_ref'] = 'responders.about_submit_list'

        if r_info.submit_list:
            contents = []
            for index, s in enumerate(r_info.submit_list):
                s_row = [s, str(index)]
                contents.append(s_row)
            page_data['submit_list','contents'] = contents
        else:
            page_data['submit_list','show'] = False
        page_data['submit_string','input_text'] = ''
        page_data['fail_page_ident:input_text'] = _ident_to_str(r_info.fail_ident)
    else:
        page_data['submit_list_description','show'] = False
        page_data['submit_list','show'] = False
        page_data['submit_string','show'] = False
        page_data['submit_info','show'] = False
        page_data['fail_page_ident','show'] = False

    # final paragraph
    page_data['final_paragraph:textblock_ref'] = _t_ref(r_info, 'final_paragraph')

    # field options
    f_options = r_info.field_options
    if not f_options['fields']:
        # no fields so no further data to input
        return page_data

    # show the fields description
    page_data['fields_description:show'] = True
    page_data['fields_description:textblock_ref'] = _t_ref(r_info, 'fields')


    if f_options['field_values'] and ( not f_options['single_field'] ):
        page_data['field_values_list:show'] = True
        page_data['add_field_value:show'] = True
        page_data['add_field_value_para:show'] = True
        # populate field_values_list
        contents = []
        field_vals = r_info.field_values_list
        for field, value in field_vals:
            f1,f2 = _field_to_string(field)
            v1,v2 = _field_to_string(value)
            if not v1:
                v1 = "' '"
            row = [f1, v1, f2]
            contents.append(row)
        if contents:
            contents.sort()
            page_data['field_values_list:contents'] = contents
        else:
            page_data['field_values_list:show'] = False
        # populate add_field_value
        if f_options['widgfields']:
            if f_options['widgfield_values']:
                 page_data['add_field_value_para:para_text'] = "Add widgfields in both the field area and in the value area"
            else:
                page_data['add_field_value_para:para_text'] = "Add widgfield and value"
        else:
            page_data['add_field_value_para:para_text'] = "Add items"
            page_data['add_field_value','label'] = "Items:"
        if f_options['empty_values_allowed']:
           page_data['add_field_value_para:para_text'] += ", empty values are allowed:"
        else:
           page_data['add_field_value_para:para_text'] += ", empty values are not allowed:"
        return
       

    if (not f_options['field_values']) and (not f_options['single_field']):
        page_data['field_list','show'] = True
        page_data['add_field','show'] = True
        # populate field_list
        contents = []
        field_vals = r_info.field_list
        for field in field_vals:
            f1,f2 = _field_to_string(field)
            row = [f1, f2]
            contents.append(row)
        if contents:
            contents.sort()
            page_data['field_list','contents'] = contents
        else:
            page_data['field_list','show'] = False
        # populate add_field
        if f_options['widgfields']:
             page_data['add_field','label'] = "Add a widgfield:"
        else:
            page_data['add_field,','label'] = "Add a string:"

    if not f_options['single_field']:
        return

    # all remaining are if a single field is required

    if not f_options['field_values']:
        # a single value is a submit text input field
        page_data[('single_field','show')] = True
        if not r_info.single_field:
            page_data[('single_field','input_text')] = ''
        else:
            page_data[('single_field','input_text')] = r_info.single_field
        return


    # remaining is for a single field and value - still to do
    # as there is currently no responder which takes a single field and value
    #????????????????????????????????????????????????????????


def submit_widgfield(skicall):
    "Sets widgfield"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not 'widget' in call_data:
        raise FailPage(message="No widgfield given", widget="widgfield_error")
    if not call_data['widget']:
        raise FailPage(message="No widgfield given", widget="widgfield_error")
    # Set the page widgfield
    try:
        call_data['pchange'] = editresponder.set_widgfield(project, pagenumber, pchange, call_data['widget'])
    except ServerError as e:
        raise FailPage(e.message)
    call_data['status'] = 'WidgField set'


def submit_alternate_ident(skicall):
    "Sets the alternate page"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not 'alternate_ident' in call_data:
        raise FailPage(message="No alternate page label given", widget="alternate")
    # Set the page alternate_ident
    try:
        call_data['pchange'] = editresponder.set_alternate_ident(project, pagenumber, pchange, call_data['alternate_ident'])
    except ServerError as e:
        raise FailPage(e.message)
    page_data['alternate','set_input_accepted'] = True
    call_data['status'] = 'Page set'



def submit_target_ident(skicall):
    "Sets the target ident"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not 'target_ident' in call_data:
        raise FailPage(message="No target ident given", widget="target")
    # Set the page target_ident
    try:
        call_data['pchange'] = editresponder.set_target_ident(project, pagenumber, pchange, call_data['target_ident'])
    except ServerError as e:
        raise FailPage(e.message)
    page_data['target','set_input_accepted'] = True
    call_data['status'] = 'Target Ident set'


def submit_validate_fail_ident(skicall):
    "Sets the validate fail ident"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not 'validate_fail_ident' in call_data:
        raise FailPage(message="No validate fail ident given", widget="validate_fail")
    # Set the page validate_fail_ident
    try:
        call_data['pchange'] = editresponder.set_validate_fail_ident(project, pagenumber, pchange, call_data['validate_fail_ident'])
    except ServerError as e:
        raise FailPage(e.message)
    page_data['validate_fail','set_input_accepted'] = True
    call_data['status'] = 'Validate Fail Ident set'


def submit_fail_ident(skicall):
    "Sets the fail ident"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not 'fail_ident' in call_data:
        raise FailPage(message="No fail ident given", widget="fail_ident_error")
    # Set the page fail_ident
    try:
        call_data['pchange'] = editresponder.set_fail_ident(project, pagenumber, pchange, call_data['fail_ident'])
    except ServerError as e:
        raise FailPage(e.message)
    call_data['status'] = 'Fail Ident set'


def add_allowed_caller(skicall):
    "Adds a new allowed caller"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not 'allowed_caller' in call_data:
        raise FailPage(message="No allowed caller given", widget="allowed_callers_error")
    # Set the page allowed caller
    try:
        call_data['pchange'] = editresponder.add_allowed_caller(project, pagenumber, pchange, call_data['allowed_caller'])
    except ServerError as e:
        raise FailPage(e.message)


def delete_allowed_caller(skicall):
    "Deletes an allowed caller"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not 'delete_allowed_caller' in call_data:
        raise FailPage(message="No allowed caller given", widget="allowed_callers_error")
    # Delete the page allowed caller
    try:
        call_data['pchange'] = editresponder.delete_allowed_caller(project, pagenumber, pchange, call_data['delete_allowed_caller'])
    except ServerError as e:
        raise FailPage(e.message)


def remove_field(skicall):
    "Deletes a field"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not 'remove_field' in call_data:
        raise FailPage(message="No field to remove given", widget="fields_error")
    # Delete the page field
    try:
        call_data['pchange'] = editresponder.remove_field(project, pagenumber, pchange, call_data['remove_field'])
    except ServerError as e:
        raise FailPage(e.message)


def add_field_value(skicall):
    "Adds a field and value"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']

    if not 'field' in call_data:
        raise FailPage(message="No field given", widget="fields_error")
    if not call_data['field']:
        raise FailPage(message="No field given", widget="fields_error")
    if not 'value' in call_data:
        raise FailPage(message="No value given", widget="fields_error")

    # if value is empty ensure empty values allowed
    if not call_data['value']:
        # get a ResponderInfo named tuple with information about the responder
        try:
            r_info = editresponder.responder_info(project, pagenumber, pchange)
        except ServerError as e:
            raise FailPage(message=e.message)
        # field options
        f_options = r_info.field_options
        if not f_options['fields']:
            raise FailPage(message="Invalid submission, this responder does not have fields", widget="fields_error")
        if not f_options['empty_values_allowed']:
            page_data['add_field_value', 'input_text1'] = call_data['field']
            page_data['add_field_value', 'set_input_accepted1'] = True
            page_data['add_field_value', 'set_input_errored2'] = True
            raise FailPage(message="Invalid submission, empty field values are not allowed", widget="fields_error")
    # Add the field and value
    try:
        call_data['pchange'] = editresponder.add_field_value(project, pagenumber, pchange, call_data['field'], call_data['value'])
    except ServerError as e:
        raise FailPage(e.message)


def add_field(skicall):
    "Adds a field"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not 'field' in call_data:
        raise FailPage(message="No field given", widget="fields_error")
    if not call_data['field']:
        raise FailPage(message="No field given", widget="fields_error")
    # Add the field
    try:
        call_data['pchange'] = editresponder.add_field(project, pagenumber, pchange, call_data['field'])
    except ServerError as e:
        raise FailPage(e.message)


def set_single_field(skicall):
    "Sets the field in a responder, which require s single field only"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not ('single_field', 'input_text') in call_data:
        raise FailPage(message="No field given", widget="fields_error")
    field = call_data[('single_field', 'input_text')]
    if not field:
        raise FailPage(message="No field given", widget="fields_error")
    # Add the field
    try:
        call_data['pchange'] = editresponder.set_single_field(project, pagenumber, pchange, field)
    except ServerError as e:
        raise FailPage(e.message)
    call_data['status'] = 'Fields set'



def delete_submit_list_string(skicall):
    "deletes an indexed string from the submit_list"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not 'delete_submit_list_string_index' in call_data:
        raise FailPage(message="No submit_list string given", widget="submit_list_error")
    try:
        # get the submit list
        submit_list = editresponder.get_submit_list(project, pagenumber, pchange)
        idx = int(call_data['delete_submit_list_string_index'])
        del submit_list[idx]
        call_data['pchange'] = editresponder.set_submit_list(project, pagenumber, pchange, submit_list)
    except ServerError as e:
        raise FailPage(e.message)


def add_submit_list_string(skicall):
    "Adds a new submit_list string"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    if not 'submit_list_string' in call_data:
        raise FailPage(message="No submit_list string given", widget="submit_list_error")
    try:
        # get the submit list
        submit_list = editresponder.get_submit_list(project, pagenumber, pchange)
        submit_list.append(call_data['submit_list_string'])
        call_data['pchange'] = editresponder.set_submit_list(project, pagenumber, pchange, submit_list)
    except ServerError as e:
        raise FailPage(e.message)


def set_validate_option(skicall):
    "Enable or disable the validate option"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    try:
        call_data['pchange'], validate_option = editresponder.toggle_validate_option(project, pagenumber, pchange)
    except ServerError as e:
        raise FailPage(e.message)        
    if validate_option:
        page_data['set_val_option','button_text'] = "Disable Validation"
        page_data['val_status','para_text'] = "Validate received field values : Enabled"
        page_data['validate_fail', 'hide'] = False
    else:
        page_data['set_val_option','button_text'] = "Enable Validation"
        page_data['val_status','para_text'] = "Validate received field values : Disabled"
        page_data['validate_fail', 'hide'] = True
    call_data['status'] = 'Validator changed'


def set_submit_option(skicall):
    "Enable or disable the submit option"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']
    pagenumber = call_data['page_number']
    pchange = call_data['pchange']
    try:
        call_data['pchange'], submit_option = editresponder.toggle_submit_option(project, pagenumber, pchange)
    except ServerError as e:
        raise FailPage(e.message)  
    call_data['status'] = 'Submit option changed'

