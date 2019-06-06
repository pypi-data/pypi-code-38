import logging
from collections import deque

from tqdm import tqdm

from onedesk.automaton.automaton import get_automaton_list_for_category
from util.models import Node, Category, Automaton
from util.util import clean_file_name

logger = logging.getLogger('main')


# expects client as a dict
def get_category_list_for_client(session, instance, client):
    logger.debug('Getting categories for client: %s', client['name'])
    response = session.get('{}/api/categories/client/{}'.format(instance, client['id']))
    logger.debug('Response: %s', response.status_code)
    if response.ok:
        return response.json()
    else:
        logger.error('Failed to get category list: %s', response.reason)
        return []


# expects category as a Category object
def get_category_list_for_category(session, instance, category):
    logger.debug('Getting categories for parent category: %s', category.name)
    response = session.get('{}/api/categories/parent/{}'.format(instance, category.id))
    logger.debug('Response: %s', response.status_code)
    if response.ok:
        return response.json()
    else:
        logger.error('Failed to get category list: %s', response.reason)
        return []


def create_category(session, instance, client, name, parent):
    headers = {'Content-Type': 'application/json;charset=UTF-8',
               'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate, br'}
    if parent is not None:
        parent_id = parent.json()['id']
    else:
        parent_id = None

    category_payload = {"name": name, "clientId": client['id'], 'parentId': parent_id}
    response = session.put('{}/api/categories/'.format(instance), headers=headers, json=category_payload)
    logger.debug('Create category response: %s', response.status_code)
    if response.ok:
        return response.json()
    else:
        logger.error('Failed to create category %s', name)
        return None


def create_parent(session, instance, client, path):
    parent = None
    for part in path.split('/')[:-1]:
        if parent is None:
            full_list = get_category_list_for_client(session, instance, client)
            category_list = []
            for item in full_list:
                if item['parentId'] is None:
                    category_list.append(item)
        else:
            category_list = get_category_list_for_category(session, instance, parent)

        exists = False
        for category in category_list:
            if category['name'] == part:
                exists = True
                parent = Category(category)
                break

        if exists:
            continue
        else:
            category = create_category(session, instance, client, part, parent)
            if category is not None:
                parent = Category(category)
            else:
                logger.error('Can not continue creating parent path')
                return None

    return parent


def get_category(session, instance, node):
    logger.debug('>>Getting category %s | %s', node.val.name, node.key)
    data = session.get('{}/api/categories/{}'.format(instance, node.key))
    logger.debug('Get category response: %s', data.status_code)
    return data.json()


def delete_category(session, instance, category):
    logging.debug('!!Deleting category %s', category['name'])
    delete_response = session.delete('{}/api/categories/{}'.format(instance, str(category['id'])))
    logging.debug('Response: %s', delete_response.status_code)


def get_category_tree(session, instance, client, root_category_name=None):
    # get all categories for the client
    category_list = get_category_list_for_client(session, instance, client)

    if root_category_name is not None:
        # if we were given a specific category to export
        for item in category_list:
            if item['name'] == root_category_name:
                category_list = [item]
                break
        if len(category_list) != 1:
            logger.warning('No category with name %s was found', root_category_name)
            return []

    # create fake root node
    # TODO come up with something better here
    root_category = Category(
        {'name': client['name'] + 'automata_root', 'id': 'root', 'clientId': '', 'parentId': None, 'deleted': False})
    root_node = Node(root_category.id, root_category)
    root_node.path = ''

    for item in category_list:
        if item['parentId'] is None:
            # identify the top level categories and add to fake root children
            category = Category(item)
            category_node = Node(category.id, category)
            category_node.path = category.name
            root_node.children.append(category_node)

    return preorder_traversal_cat(session, instance, root_node)


# Utility function to return the preorder list of the given N-Ary Tree
def preorder_traversal_cat(session, instance, root_node):
    stack = deque([])  # 'stack' holds the nodes to be visited
    preorder = []  # 'preorder' contains all visited keys
    preorder_nodes = []  # 'preorder_nodes' contains all visited nodes

    # add all top level nodes to the stack and visited lists
    for child in root_node.children:
        stack.append(child)
        preorder.append(child.path)
        preorder_nodes.append(child)

    while len(stack) > 0:
        finished = 0  # 'finished' checks whether all the child nodes have been visited
        # get top node from the stack
        top_node = stack[len(stack) - 1]

        if type(top_node.val) is Category and len(top_node.children) == 0:
            # get children for category nodes
            top_node.children = get_children_for_category(session, instance, top_node)

        if len(top_node.children) == 0:
            # CASE 1 - If top of the stack is a leaf node then pop it from the stack
            stack.pop()
        else:
            # CASE 2 - If top of the stack is parent with children
            for child in top_node.children:
                if child.path not in preorder:
                    # As soon as an unvisited child is found (left to right) push it to the stack
                    finished = 1
                    stack.append(child)
                    preorder.append(child.path)
                    preorder_nodes.append(child)
                    break

            # If all child nodes from left to right of a parent have been visited then pop it from the stack
            if finished == 0:
                stack.pop()

    return preorder_nodes


def get_children_for_category(session, instance, node):
    children = []
    # get categories under top node
    category_list = get_category_list_for_category(session, instance, node.val)
    # get automata under top node
    automaton_list = get_automaton_list_for_category(session, instance, node.val)

    for child in tqdm(category_list, desc='Getting categories for {}'.format(node.path)):
        category = Category(child)
        category_node = Node(category.id, category)
        category_node.path = node.path + "/" + clean_file_name(category.name)
        category_node.parent = node
        children.append(category_node)

    for child in tqdm(automaton_list, desc='Getting automata for {}'.format(node.path)):
        automaton = Automaton(child)
        automaton_node = Node(automaton.id, automaton)
        automaton_node.path = node.path + "/" + clean_file_name(automaton.name)
        automaton_node.parent = node
        children.append(automaton_node)

    return children
