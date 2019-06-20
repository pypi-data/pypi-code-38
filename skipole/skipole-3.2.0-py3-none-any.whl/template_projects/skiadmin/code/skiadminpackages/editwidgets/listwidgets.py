

"Functions implementing admin page editing"


import re

from skipole import skilift
from skipole.skilift import editwidget

from skipole import ServerError, FailPage, ValidateError, GoTo

# a search for anything none-alphanumeric and not an underscore
_AN = re.compile('[^\w]')


def retrieve_module_list(skicall):
    "this call is to retrieve data for listing widget modules"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # Fill in header
    page_data[("adminhead","page_head","large_text")] = "Choose module"

    # as this page chooses a module, clear any previous chosen module and widget class
    if 'module' in call_data:
        del call_data['module']
    if 'widgetclass' in call_data:
        del call_data['widgetclass']

    # table of widget modules

    # col 0 is the visible text to place in the link,
    # col 1 is the get field of the link
    # col 2 is the get field of the link
    # col 3 is the reference string of a textblock to appear in the column adjacent to the link
    # col 4 is text to appear if the reference cannot be found in the database
    # col 5 normally empty string, if set to text it will replace the textblock

    contents = []

    modules_tuple = editwidget.widget_modules()

    for name in modules_tuple:
        ref = 'widgets.' + name + '.module'
        notfound = 'Textblock reference %s not found' % ref
        contents.append([name, name, '', ref, notfound, ''])

    page_data[("modules","link_table")] = contents


def retrieve_widgets_list(skicall):
    "this call is to retrieve data for listing widgets in a module"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # Fill in header
    call_data['extend_nav_buttons'].append(["list_widget_modules", "Modules", True, ''])

    if 'chosen_module' in call_data:
        module_name = call_data['chosen_module']
    elif 'module' in call_data:
        module_name = call_data['module']
    else:
        raise FailPage("Module not identified")

    modules_tuple = editwidget.widget_modules()

    if module_name not in modules_tuple:
        raise FailPage("Module not identified")

    # set module into call_data
    call_data['module'] = module_name

    page_data[("adminhead","page_head","large_text")] = "Widgets in module %s" % (module_name,)
    page_data[('moduledesc','textblock_ref')] = 'widgets.' + module_name + '.module'

    if 'widgetclass' in call_data:
        # as this page chooses a widget, clear any previous chosen widget class
        del call_data['widgetclass']

    # table of widgets

    # col 0 is the visible text to place in the link,
    # col 1 is the get field of the link
    # col 2 is the get field of the link
    # col 3 is the reference string of a textblock to appear in the column adjacent to the link
    # col 4 is text to appear if the reference cannot be found in the database
    # col 5 normally empty string, if set to text it will replace the textblock

    widget_list = editwidget.widgets_in_module(module_name)
    contents = []
    for widget in widget_list:
        ref = ".".join(("widgets", module_name, widget.classname))
        notfound = 'Textblock reference %s not found' % ref
        classname = widget.classname
        contents.append([classname, classname, '', ref, notfound, ''])

    page_data[("widgets","link_table")] = contents


def retrieve_new_widget(skicall):
    "this call is to retrieve data for displaying a new widget"

    call_data = skicall.call_data
    page_data = skicall.page_data

    # Fill in header
    call_data['extend_nav_buttons'].extend([["list_widget_modules", "Modules", True, ''], ["back_widget_list", "Widgets", True, '']])

    if 'module' not in call_data:
        raise FailPage("Module not identified")

    module_name = call_data['module']
    modules_tuple = editwidget.widget_modules()
    if module_name not in modules_tuple:
        raise FailPage("Module not identified")

    if 'chosen_widget' in call_data:
        widget_class_name = call_data['chosen_widget']
    elif 'widgetclass' in call_data:
        widget_class_name = call_data['widgetclass']
    else:
        raise FailPage("Widget not identified")


    widget_list = editwidget.widgets_in_module(module_name)
    widget_dict = {widgetdescription.classname : widgetdescription for widgetdescription in widget_list}
    
    if widget_class_name not in widget_dict:
        raise FailPage("Widget not identified")

    widg = widget_dict[widget_class_name]
    # widg is a WidgetDescription named tuple

    page_data[("adminhead","page_head","large_text")] = "Create widget of type %s" % (widget_class_name,)


    ref = "widgets." + widg.modulename + "." + widg.classname
    full_textref = ref + '.full'   # the widget full reference string

    adminaccesstextblocks = skilift.get_accesstextblocks(skicall.project)

    if adminaccesstextblocks.textref_exists(full_textref):
        page_data['widgetdesc','textblock_ref'] = full_textref
    else:
        page_data['widgetdesc','textblock_ref'] = ref

    field_contents = []

    for field_argument in widg.fields:
        if field_argument == 'show':
            field_contents.append([field_argument, 'widgets.show'])
        elif field_argument == 'widget_class':
            field_contents.append([field_argument, 'widgets.widget_class'])
        elif field_argument == 'widget_style':
            field_contents.append([field_argument, 'widgets.widget_style'])
        elif field_argument == 'show_error':
            field_contents.append([field_argument, 'widgets.show_error'])
        elif field_argument == 'clear_error':
            field_contents.append([field_argument, 'widgets.clear_error'])
        else:
            field_contents.append([field_argument, ref + '.' + field_argument])

    page_data[('fieldtable','contents')] = field_contents

    if widg.containers:
        page_data[('containerdesc','show')] = True

    # set widget class name into call_data
    call_data['widgetclass'] = widget_class_name

    # display the widget html
    page_data[('widget_code','pre_text')] = widg.illustration


def create_new_widget(skicall):
    "this call is to create and insert a new widget, goes on to widget edit"

    call_data = skicall.call_data
    page_data = skicall.page_data

    project = call_data['editedprojname']

    if 'module' not in call_data:
        raise FailPage("Module not identified")
    if 'widgetclass' not in call_data:
        raise FailPage("Widget not identified")
    if 'location' not in call_data:
        raise FailPage("Location of new widget has not been understood")

    if 'new_widget_name' not in call_data:
        raise FailPage("Widget name missing")
    new_name=call_data['new_widget_name']
    if not new_name:
        raise FailPage("Invalid name")
    new_lower_name = new_name.lower()
    if (new_lower_name == 'body') or (new_lower_name == 'head') or (new_lower_name == 'svg')  or (new_lower_name == 'show_error'):
        raise FailPage(message="Unable to create the widget, the name given is reserved")
    if _AN.search(new_name):
        raise FailPage(message="Invalid name, alphanumeric and underscore only")
    if new_name[0] == '_':
        raise FailPage(message="Invalid name, must not start with an underscore")
    if new_name.isdigit():
        raise FailPage(message="Unable to create the widget, the name must include some letters")

    if 'new_widget_brief' not in call_data:
        raise FailPage("Widget description missing")
    new_brief = call_data['new_widget_brief']

    if 'page_number' in call_data:
        try:
            call_data['pchange'], new_location =  editwidget.create_new_widget_in_page(project,
                                                                         call_data['page_number'],
                                                                         call_data['pchange'],
                                                                         call_data['location'],
                                                                         call_data['module'],
                                                                         call_data['widgetclass'],
                                                                         new_name,
                                                                         new_brief)
        except ServerError as e:
            raise FailPage(e.message)
        call_data['widget_name'] = new_name
        call_data['status'] = "Widget created"
        return

    if 'section_name' in call_data:
        try:
            call_data['schange'], new_location =  editwidget.create_new_widget_in_section(project,
                                                                            call_data['section_name'],
                                                                            call_data['schange'],
                                                                            call_data['location'],
                                                                            call_data['module'],
                                                                            call_data['widgetclass'],
                                                                            new_name,
                                                                            new_brief)
        except ServerError as e:
            raise FailPage(e.message)
        call_data['widget_name'] = new_name
        call_data['status'] = "Widget created"
        return

    raise FailPage("Either a page or section must be specified")


