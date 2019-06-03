"""Util to build user readable queries
"""
from core_explore_example_app.utils.mongo_query import get_parent_name
from core_explore_example_app.utils.query_builder import get_element_value, get_element_comparison
from core_parser_app.components.data_structure_element import api as data_structure_element_api


def build_pretty_criteria(element_name, comparison, value, is_not=False):
    """Returns a pretty representation of the criteria

    Args:
        element_name:
        comparison:
        value:
        is_not:

    Returns:

    """
    pretty_criteria = ""

    if is_not:
        pretty_criteria += "NOT("

    pretty_criteria += element_name

    if comparison == "lt":
        pretty_criteria += " &lt; "
    elif comparison == "lte":
        pretty_criteria += " &le; "
    elif comparison == "=":
        pretty_criteria += "="
    elif comparison == "gte":
        pretty_criteria += " &ge; "
    elif comparison == "gt":
        pretty_criteria += " &gt; "
    elif comparison == "is":
        pretty_criteria += " is "
    elif comparison == "like":
        pretty_criteria += " like "

    if value:
        pretty_criteria += value
    else:
        pretty_criteria += ' &ldquo;  &ldquo;'

    if is_not:
        pretty_criteria += ")"

    return pretty_criteria


def build_query_pretty_criteria(query_value, is_not):
    """Returns a pretty representation of the query

    Args:
        query_value:
        is_not:

    Returns:

    """
    if is_not:
        return "NOT(" + query_value + ")"
    else:
        return query_value


def build_or_pretty_criteria(query, criteria):
    """Returns a pretty representation of the OR

    Args:
        query:
        criteria:

    Returns:

    """
    return "(" + query + " OR " + criteria + ")"


def build_and_pretty_criteria(query, criteria):
    """Returns a pretty representation of the AND

    Args:
        query:
        criteria:

    Returns:

    """
    return "(" + query + " AND " + criteria + ")"


def fields_to_pretty_query(form_values):
    """Transforms fields from the HTML form into pretty representation

    Args:
        form_values:

    Returns:

    """

    query = ""

    for field in form_values:
        bool_comp = field['operator']
        if bool_comp == 'NOT':
            is_not = True
        else:
            is_not = False

        # get element value
        value = get_element_value(field)
        # get comparison operator
        comparison = get_element_comparison(field)

        element_type = field.get('type', None)
        if element_type == "query":
            criteria = build_query_pretty_criteria(field['name'], is_not)
        else:
            criteria = build_pretty_criteria(field['name'], comparison, value, is_not)

        if bool_comp == 'OR':
            query = build_or_pretty_criteria(query, criteria)
        elif bool_comp == 'AND':
            query = build_and_pretty_criteria(query, criteria)
        else:
            if form_values.index(field) == 0:
                query += criteria
            else:
                query = build_and_pretty_criteria(query, criteria)

    return query


def sub_elements_to_pretty_query(form_values, namespaces):
    """Transforms HTML fields in a user readable query

    Args:
        form_values:
        namespaces:

    Returns:

    """
    # get the parent path using the first element of the list
    parent_name = get_parent_name(form_values[0]['id'], namespaces)

    list_criteria = []
    for i in range(0, len(form_values)):
        field = form_values[i]
        if field['selected'] is True:
            bool_comp = field['operator']
            if bool_comp == 'NOT':
                is_not = True
            else:
                is_not = False

            data_structure_element = data_structure_element_api.get_by_id(field['id'])
            element_name = data_structure_element.options['name']
            value = get_element_value(field)
            comparison = get_element_comparison(field)

            criteria = build_pretty_criteria(element_name, comparison, value, is_not)

            list_criteria.append(criteria)

    query = "{0}({1})".format(parent_name, ", ".join(list_criteria))

    return query
