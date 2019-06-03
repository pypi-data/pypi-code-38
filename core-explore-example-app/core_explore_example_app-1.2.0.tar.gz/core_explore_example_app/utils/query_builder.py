"""Utils for the query builder
"""
from os.path import join

from django.template import loader

from core_explore_example_app.utils.xml import get_enumerations
from xml_utils.xsd_types.xsd_types import get_xsd_numbers


class BranchInfo:
    """ Store information about a branch from the xml schema while it is being processed for field selection
    """
    def __init__(self, keep_the_branch=False, selected_leaves=None):
        self.keep_the_branch = keep_the_branch
        self.selected_leaves = selected_leaves if selected_leaves is not None else []

    def add_selected_leaf(self, leaf_id):
        self.selected_leaves.append(leaf_id)
        self.keep_the_branch = True


# Util functions

def prune_html_tree(html_tree):
    """ Create a custom HTML tree from fields chosen by the user

    Args:
        html_tree:

    Returns:

    """
    any_branch_checked = False

    list_ul = html_tree.findall("./ul")
    for ul in list_ul:
        branch_info = prune_ul(ul)
        if branch_info.keep_the_branch:
            any_branch_checked = True

    return any_branch_checked


def prune_ul(ul):
    """ Process the ul element of an HTML list

    Args:
        ul:

    Returns:

    """
    list_li = ul.findall("./li")
    branch_info = BranchInfo()

    for li in list_li:
        li_branch_info = prune_li(li)
        if li_branch_info.keep_the_branch:
            branch_info.keep_the_branch = True
        branch_info.selected_leaves.extend(li_branch_info.selected_leaves)

    checkbox = ul.find("./input[@type='checkbox']")
    if checkbox is not None:
        if 'value' in checkbox.attrib and checkbox.attrib['value'] == 'true':
            # set element class
            parent_li = ul.getparent()
            element_id = parent_li.attrib['class']
            add_selection_attributes(parent_li, 'element', element_id)
            # tells to keep this branch until this leaf
            branch_info.add_selected_leaf(element_id)

    if not branch_info.keep_the_branch:
        add_selection_attributes(ul, 'none')

    return branch_info


def prune_li(li):
    """ Process the li element of an HTML list

    Args:
        li:

    Returns:

    """
    list_ul = li.findall("./ul")
    branch_info = BranchInfo()

    if len(list_ul) != 0:
        selected_leaves = []
        for ul in list_ul:
            ul_branch_info = prune_ul(ul)
            if ul_branch_info.keep_the_branch:
                branch_info.keep_the_branch = True
            selected_leaves.extend(ul_branch_info.selected_leaves)

        # sub element queries available when more than one selected elements under the same element
        if len(selected_leaves) > 1:
            # not for the choices
            if li[0].tag != 'select':
                # TODO: check if test useful
                if 'select_class' not in li.attrib:
                    leaves_id = ' '.join(selected_leaves)
                    add_selection_attributes(li, 'parent', leaves_id)
        if not branch_info.keep_the_branch:
            add_selection_attributes(li, 'none')

        return branch_info
    else:
        try:
            checkbox = li.find("./input[@type='checkbox']")
            if checkbox.attrib['value'] == 'false':
                add_selection_attributes(li, 'none')
                return branch_info
            else:
                element_id = li.attrib['class']
                add_selection_attributes(li, 'element', element_id)
                # tells to keep this branch until this leaf
                branch_info.add_selected_leaf(element_id)
                return branch_info
        except:
            return branch_info


def sub_element_query_li(li, selected_leaves):
    """ Update li with sub-element query attributes

    Args:
        li:
        selected_leaves:

    Returns:

    """
    # not for the choices
    if li[0].tag != 'select':
        # TODO: check if test useful
        if 'select_class' not in li.attrib:
            leaves_id = ' '.join(selected_leaves)
            # set element class
            li.attrib['select_class'] = 'parent'
            li.attrib['select_id'] = leaves_id


def add_selection_attributes(element, select_class, select_id=None):
    """ Add css attribute to selected element

    Args:
        element:
        select_class:
        select_id:

    Returns:

    """
    element.attrib['select_class'] = select_class
    if select_id is not None:
        element.attrib['select_id'] = select_id


# Rendering functions


def render_yes_or_not():
    """ Return a string that represents an html select with yes or not options

    Returns:

    """
    return _render_template(join('core_explore_example_app', 'user', 'query_builder', 'yes_no.html'))


def render_and_or_not():
    """ Return a string that represents an html select with AND, OR, NOT options

    Returns:

    """
    return _render_template(join('core_explore_example_app', 'user', 'query_builder', 'and_or_not.html'))


def render_numeric_select():
    """ Return a string that represents an html select with numeric comparisons

    Returns:

    """
    return _render_template(join('core_explore_example_app', 'user', 'query_builder', 'numeric_select.html'))


def render_value_input():
    """ Return an input to type a value

    Returns:

    """
    return _render_template(join('core_explore_example_app', 'user', 'query_builder', 'input.html'))


def render_string_select():
    """ Return an input to type a value

    Returns:

    """
    return _render_template(join('core_explore_example_app', 'user', 'query_builder', 'string_select.html'))


def render_initial_form():
    """ Render the initial Query Builder

    Returns:

    """
    return _render_template(join('core_explore_example_app', 'user', 'query_builder', 'initial_form.html'))


def render_remove_button():
    """ Return html of a remove button

    Returns:

    """
    return _render_template(join('core_explore_example_app', 'user', 'query_builder', 'remove.html'))


def render_add_button():
    """ Return html of an add button

    Returns:

    """
    return _render_template(join('core_explore_example_app', 'user', 'query_builder', 'add.html'))


def render_enum(enums):
    """ Return html select from an enumeration

    Args:
        enums:

    Returns:

    """
    context = {
        'enums': enums,
    }
    return _render_template(join('core_explore_example_app', 'user', 'query_builder', 'enum.html'), context)


def render_new_query(tag_id, query, is_first=False):
    """ Return an html string for a new query

    Args:
        tag_id:
        query:
        is_first:

    Returns:

    """
    context = {
        'tagID': tag_id,
        'query': query,
        'first': is_first
    }
    return _render_template(join('core_explore_example_app', 'user', 'query_builder', 'new_query.html'), context)


def render_new_criteria(tag_id):
    """ Return an html string for a new query

    Args:
        tag_id:

    Returns:

    """
    context = {
        'tagID': tag_id,
    }
    return _render_template(join('core_explore_example_app', 'user', 'query_builder', 'new_criteria.html'), context)


def render_sub_elements_query(parent_name, form_fields):
    """ Return an html string for a query on sub-elements

    Args:


    Returns:

    """
    context = {
        'parent_name': parent_name,
        'form_fields': form_fields,
    }
    return _render_template(join('core_explore_example_app', 'user', 'query_builder', 'sub_elements_query.html'),
                            context)


def get_element_value(element_field):
    """ Get value from field

    Args:
        element_field:

    Returns:

    """
    return element_field['value'] if 'value' in element_field else None


def get_element_comparison(element_field):
    """ Get comparison operator from field

    Args:
        element_field:

    Returns:

    """
    return element_field['comparison'] if 'comparison' in element_field else 'is'


def get_user_inputs(element_type, data_structure_element, default_prefix):
    """ Get user inputs from element type

    Args:
        element_type:
        data_structure_element:
        default_prefix:

    Returns:

    """
    try:
        if element_type is not None and element_type.startswith("{0}:".format(default_prefix)):
            # numeric
            if element_type in get_xsd_numbers(default_prefix):
                user_inputs = render_numeric_select() + render_value_input()
            # string
            else:
                user_inputs = render_string_select() + render_value_input()
        else:
            # enumeration
            enums = get_enumerations(data_structure_element)
            user_inputs = render_enum(enums)
    except:
        # default renders string form
        user_inputs = render_string_select() + render_value_input()

    return user_inputs


def _render_template(template_path, context=None):
    """ Return an HTML string rendered from the template

    Args:
        template_path:

    Returns:

    """
    if context is None:
        context = {}
    template = loader.get_template(template_path)
    return template.render(context)
