import json
import logging
from collections import deque
from pathlib import Path

from util.models import Node, Category, Automaton, ExportedAutomaton

logger = logging.getLogger('main')


# Utility function to return the preorder list of the given N-Ary Tree
def preorder_traversal_dir(directory, root_node):
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

        # if the top_node contains a Category we get its children
        if type(top_node.val) is Category and len(top_node.children) == 0:
            top_node.children = get_children_for_directory(directory, top_node)

        if len(top_node.children) == 0:
            # CASE 1- If top of the stack is a leaf node then pop it from the stack
            stack.pop()
        else:
            # CASE 2- If top of the stack is parent with children
            for child in top_node.children:
                if child.path not in preorder:
                    # As soon as an unvisited child is found (left to right) push it to stack and store it in preorder
                    finished = 1
                    stack.append(child)
                    preorder.append(child.path)
                    preorder_nodes.append(child)
                    break

            # If all child nodes from left to right of a parent have been visited then pop it from the stack
            if finished == 0:
                stack.pop()

    return preorder_nodes


def get_children_for_directory(directory, node):
    children = []

    for child in Path(directory, node.path).iterdir():
        child_ob = None
        if child.suffix == '.json' and child.is_file():
            child_dict = read_json_file(child)
            if 'latestAutomatonVersion' in child_dict:
                child_ob = Automaton(child_dict)
            elif 'automatonFlow' in child_dict:
                child_ob = ExportedAutomaton(child_dict)
        elif child.is_dir():
            logger.debug('Reading directory %s', child.absolute())
            child_ob = Category({'name': child.name,
                                 'id': '',
                                 'clientId': '',
                                 'parentId': '',
                                 'deleted': False})

        if child_ob is not None:
            # create Node to contain object and add to top_node children
            child_node = Node(child_ob.id, child_ob)
            child_node.path = node.path + '/' + child_ob.name
            child_node.parent = node
            children.append(child_node)

    return children


def get_directory_tree(directory):
    logger.debug('Reading directory %s', directory)

    # create fake root node
    root_category = Category(
        {'name': 'automata_root',
         'id': 'root',
         'clientId': '',
         'parentId': None,
         'deleted': False}
    )
    root_node = Node(root_category.id, root_category)
    root_node.path = directory.absolute()

    for child in directory.iterdir():
        child_ob = None
        if child.suffix == '.json' and child.is_file():
            child_dict = read_json_file(child)
            if 'latestAutomatonVersion' in child_dict:
                child_ob = Automaton(child_dict)
            elif 'automatonFlow' in child_dict:
                child_ob = ExportedAutomaton(child_dict)
        elif child.is_dir():
            logger.debug('Reading directory %s', child.absolute())
            child_ob = Category({'name': child.name,
                                 'id': '',
                                 'clientId': '',
                                 'parentId': '',
                                 'deleted': False})

        if child_ob is not None:
            child_node = Node(child_ob.id, child_ob)
            child_node.path = child.name
            root_node.children.append(child_node)

    return preorder_traversal_dir(directory, root_node)


def read_json_file(file):
    logger.debug('Reading file %s', file.absolute())
    return json.loads(file.read_text())


def write_json_file(file, data):
    logger.debug('Writing file %s', file.absolute())
    file.write_text(json.dumps(data, sort_keys=True, indent=4))


def clean_file_name(file_name):
    return file_name.strip() \
        .replace("/", "_") \
        .replace("\\", "_") \
        .replace(":", "_") \
        .replace(";", "_") \
        .replace("?", "_") \
        .replace("!", "_") \
        # .replace(" ", "_")
