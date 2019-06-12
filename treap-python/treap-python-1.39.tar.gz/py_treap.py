#!/usr/bin/env python

# pylint: disable=superfluous-parens

'''
Provides a treap module - specifically, the class that describes the overall treap, not the nodes.

A treap is a datastructure that's kind of half way between a heap and a binary search tree
'''

# Editor width - you must be at least this tall to enjoy this ride #################################################################

# Appears to be an excellent reference on treaps in java:
# http://users.cis.fiu.edu/~weiss/dsaajava/Code/DataStructures
# However, I'm not certain the remove method is correct
#
# Another nice reference on treaps in java:
# https://blog.eldslott.org/2009/04/25/treap-implementation-in-java/
# It doesn't seem to mention removals, but it shows rotations nicely
#
# A pretty complete-looking java implementation of treaps:
# http://www.nada.kth.se/~snilsson/public/code/treap/source/Treap.java
# It has what looks like a nice remove.  However, I wound up using something based on Weiss's code with two additional if's instead.



import sys
import math

# actually, it's a little faster with the standard random module than the lcgrng module; although random is a more time
# consuming algorithm, it's coded in C.
import random as random_module

PRIORITY_SIZE = 0x7fffffff


# this is all "hands off" to a client of the module

SENTINEL = object()


class treap_node(object):
    '''Hold a single node of a treap'''






    __slots__ = ('priority', 'key', 'value', 'left', 'right')

    def __init__(self):
        self.priority = int(random_module.random() * PRIORITY_SIZE)
        self.key = None
        self.value = None
        self.left = None
        self.right = None

    def to_dot(self, initial=True, file_=sys.stdout, visited=None):
        """Generate a dot file describing this tree"""

        if visited is None:
            visited = set()
        if initial:
            file_.write('digraph G {\n')
        this_node = '%s %s' % (id(self), str(self))
        if this_node in visited:
            return
        visited.add(this_node)
        if self.left is not None:
            file_.write('   "%s" -> "%s %s" [ label="left" ]\n' % (this_node, id(self.left), str(self.left)))
            self.left.to_dot(initial=False, file_=file_, visited=visited)
        if self.right is not None:
            file_.write('   "%s" -> "%s %s" [ label="right" ]\n' % (this_node, id(self.right), str(self.right)))
            self.right.to_dot(initial=False, file_=file_, visited=visited)
        if initial:
            file_.write('}\n')

    def check_tree_invariant(self):
        '''Check the tree invariant'''
        if self.left is not None:
            assert self.key > self.left.key
            assert self.left.check_tree_invariant()
        if self.right is not None:
            assert self.key < self.right.key
            assert self.right.check_tree_invariant()
        return True

    def check_heap_invariant(self):
        '''Check the heap invariant'''
        # I kinda thought it was supposed to be <, but clearly that won't work with random priorities
        if self.left is not None:
            assert self.priority <= self.left.priority
            assert self.left.check_heap_invariant()
        if self.right is not None:
            assert self.priority <= self.right.priority
            assert self.right.check_heap_invariant()
        return True

    def find_node(self, key):
        '''Look up a node in the treap: return the containing node'''

        current = self

        while True:
            if current is None:
                raise KeyError
            elif key < current.key:
                current = current.left
            elif key > current.key:
                current = current.right
            else:
                # equal
                return current

    def check_invariants(self):
        '''Check the tree and heap invariants'''
        assert self.check_tree_invariant()
        assert self.check_heap_invariant()
        return True

    def insert(self, node, key, value, priority):
        '''Insert a node - just call the fast version'''
        return self.pyx_insert(node, key, value, priority)

    def pyx_insert(self, node, key, value, priority):
        '''Insert a node - this is the fast version'''
        # We arbitrarily ditch duplicate values, but I believe we could just save them in a list.
        # We probably should have a series of classes via a class factory that sets class variables to
        # distinguish the priority max and whether we store duplicates.
        if node is None:
            # adding a node, increasing the treap length by 1
            node = treap_node()
            if priority:
                node.priority = priority
            node.key = key
            node.value = value
            return (1, node)
        elif key < node.key:
            (length_delta, node.left) = self.pyx_insert(node.left, key, value, priority)
            if node.left.priority < node.priority:
                node = self.rotate_with_left_child(node)
            return (length_delta, node)
        elif key > node.key:
            (length_delta, node.right) = self.pyx_insert(node.right, key, value, priority)
            if node.right.priority < node.priority:
                node = self.rotate_with_right_child(node)
            return (length_delta, node)
        else:
            # must be equal - replacing a node - does not change the treap length
            node.key = key
            node.value = value
            return (0, node)

    def remove(self, node, key):
        '''Remove a node - just call the fast version'''
        return self.pyx_remove(node, key)

    def pyx_remove(self, node, key):
        '''Remove a node - this is the fast version'''
        found = False
        if node is not None:
            if key < node.key:
                (found, node.left) = self.pyx_remove(node.left, key)
            elif key > node.key:
                (found, node.right) = self.pyx_remove(node.right, key)
            else:
                # Match found
                # these two tests for emptiness don't appear to be in http://users.cis.fiu.edu/~weiss/dsaajava/Code/DataStructures
                if node.left is None:
                    return (True, node.right)
                if node.right is None:
                    return (True, node.left)
                if node.left.priority < node.right.priority:
                    node = self.rotate_with_left_child(node)
                else:
                    node = self.rotate_with_right_child(node)

                # Continue on down
                if node is not None:
                    (found, node) = self.pyx_remove(node, key)
                else:
                    # At a leaf
                    node.left = None
        return (found, node)

    def remove_min(self, node):
        '''Remove the lowest node below us'''
        if not (node is None):
            if not (node.left is None):
                (node.left, result) = self.remove_min(node.left)
            else:
                # Minimum found
                return (node.right, (node.key, node.value))
        return (node, result)

    def remove_max(self, node):
        '''Remove the highest node below us'''
        if not (node is None):
            if not (node.right is None):
                (node.right, result) = self.remove_max(node.right)
            else:
                # maximum found
                return (node.left, (node.key, node.value))
        return (node, result)

    def rotate_with_left_child(self, node):
        # pylint: disable=R0201
        # R0201: Cython (Mar 28, 2011) doesn't like decorators on cdef's , so we disable the "method could be a function" warning
        '''This is a treap thing - rotate to rebalance'''
        temp = node.left
        node.left = temp.right
        temp.right = node
        node = temp
        return node

    def rotate_with_right_child(self, node):
        # pylint: disable=R0201
        # R0201: Cython (Mar 28, 2011) doesn't like decorators on cdef's , so we disable the "method could be a function" warning
        '''This is a treap thing - rotate to rebalance'''
        temp = node.right
        node.right = temp.left
        temp.left = node
        node = temp
        return node

    def detailed_inorder_traversal(self, visit, depth=0, from_left=0):
        '''Do an inorder traversal - with lots of parameters'''
        if self.left is not None:
            self.left.detailed_inorder_traversal(visit, depth + 1, from_left * 2)
        visit(self, self.key, self.value, depth, from_left)
        if self.right is not None:
            self.right.detailed_inorder_traversal(visit, depth + 1, from_left * 2 + 1)

    def inorder_traversal(self, visit):
        '''Do an inorder traversal - without lots of parameters'''
        if self.left is not None:
            self.left.inorder_traversal(visit)
        visit(self.key, self.value)
        if self.right is not None:
            self.right.inorder_traversal(visit)

    def __str__(self):
        return '%s/%s/%s' % (self.key, self.priority, self.value)

    def find_min_node(self):
        '''Find the lowest node in the treap'''
        current = self

        if current is None:
            raise KeyError

        while current.left is not None:
            current = current.left

        return current

    def find_max_node(self):
        '''Find the highest node in the treap'''
        current = self

        if current is None:
            raise KeyError

        while current.right is not None:
            current = current.right

        return current

# Each element is stored in a node in a tree, and each node contains an integer and two references, one to the left
# subtree and one to the right subtree.

# We need to increase the recurision limit to fend off the randomization trolls from causing an over-deep recursion
# In practice, this'll be very unlikely, extremely unlikely, unless the client of this package chooses a
# small priority_size and saves a large number of values
MIN_HEAP_SIZE = 100000
if sys.getrecursionlimit() < MIN_HEAP_SIZE:
    sys.setrecursionlimit(MIN_HEAP_SIZE)


def pad_to(string, length):
    '''Pad a string to a specified length'''
    return string + '_' * (length - len(string) - 1) + ' '


def center(string, field_use_width, field_avail_width):
    '''Center a string within a given field width'''
    field_use = (string + '_' * (field_use_width - 1))[:field_use_width - 1]
    pad_width = (field_avail_width - len(field_use)) / 2.0
    result = ' ' * int(pad_width) + field_use + ' ' * int(math.ceil(pad_width))
    return result


# this is the public portion
class treap(object):
    '''The treap class - or rather, the non-node, treap-proper'''
    def __init__(self):
        self.root = None
        self.length = 0

    def to_dot(self, file_=sys.stdout):
        '''Output this tree as a dot file'''
        self.root.to_dot(file_=file_)

    def find_node(self, key):
        '''Return the node associated with key, not just its value'''

        return self.root.find_node(key)

    # __bool__ is the python 3 name of the special method, while __nonzero__ is the python 2 name
    def __bool__(self):
        return self.root is not None

    __nonzero__ = __bool__

    def __len__(self):
        return self.length

    def _slow_len(self):
        '''Compute the length of the treap in a slow but accurate way'''
        count = 0

        for dummy in self.values():
            count += 1

        return count

    def __setitem__(self, key, value, priority=None):
        '''Insert a node in the treap'''
        if self.root is None:
            self.root = treap_node()
            self.root.key = key
            self.root.value = value
            if priority:
                self.root.priority = priority

            self.length = 1
        else:
            (length_delta, self.root) = self.root.insert(self.root, key, value, priority)
            assert length_delta in [0, 1]
            self.length += length_delta

    insert = __setitem__

    def __delitem__(self, key):
        '''Remove a node from the treap'''
        if self.root is not None:
            (found, self.root) = self.root.remove(self.root, key)
            if found:
                self.length -= 1
            else:
                raise KeyError
        else:
            raise KeyError

    remove = __delitem__

    def remove_min(self):
        '''Remove the lowest node in the treap'''
        if self.root is not None:
            (self.root, result) = self.root.remove_min(self.root)
            if not (result is None):
                self.length -= 1
            return result
        else:
            raise KeyError

    def remove_max(self):
        '''Remove the largest node in the treap'''
        if self.root is not None:
            (self.root, result) = self.root.remove_max(self.root)
            if not (result is None):
                self.length -= 1
            return result
        else:
            raise KeyError

    def __getitem__(self, key):
        '''Look up a node in the treap: return the value'''
        current = self.root

        while True:
            if current is None:
                raise KeyError
            elif key < current.key:
                current = current.left
            elif key > current.key:
                current = current.right
            else:
                # equal
                return current.value

    def get_key(self, key):
        '''Look up a _key_ in the treap by key: return the key'''
        current = self.root

        while True:
            if current is None:
                raise KeyError
            elif key < current.key:
                current = current.left
            elif key > current.key:
                current = current.right
            else:
                # equal
                return current.key

    find = __getitem__

    def __contains__(self, key):
        try:
            dummy = self[key]
        except KeyError:
            return False
        else:
            return True

    def find_min(self):
        '''Find the lowest key in the treap'''
        current = self.root

        if current is None:
            raise KeyError

        while current.left is not None:
            current = current.left

        return current.key

    def find_max(self):
        '''Find the highest key in the treap'''
        current = self.root

        if current is None:
            raise KeyError

        while current.right is not None:
            current = current.right

        return current.key

    def predecessor(self, node):
        # Based on successor method above
        '''Find the predecessor of index in the treap'''

        current = self.root

        if current is None:
            raise KeyError

        if node.left is not None:
            node = node.left.find_max_node()
            return node

        pred = SENTINEL

        while current is not None:
            if node.key > current.key:
                pred = current
                current = current.right
            elif node.key < current.key:
                current = current.left
            else:
                break

        if pred is SENTINEL:
            raise LookupError

        return pred

    def successor(self, node):
        # Based on method 2 at http://www.geeksforgeeks.org/inorder-successor-in-binary-search-tree/
        '''Find the successor of index in the treap'''

        current = self.root

        if current is None:
            raise KeyError

        if node.right is not None:
            node = node.right.find_min_node()
            return node

        succ = SENTINEL

        while current is not None:
            if node.key < current.key:
                succ = current
                current = current.left
            elif node.key > current.key:
                current = current.right
            else:
                break

        if succ is SENTINEL:
            raise LookupError

        return succ

    def inorder_traversal(self, visit):
        '''Perform an inorder traversal of the treap'''
        if self.root is not None:
            self.root.inorder_traversal(visit)

    def detailed_inorder_traversal(self, visit):
        '''Perform an inorder traversal of the treap, passing a little more detail to the visit function at each step'''
        if self.root is not None:
            self.root.detailed_inorder_traversal(visit)

    def check_tree_invariant(self):
        '''Check the tree invariant'''
        if self.root is None:
            return True
        return self.root.check_tree_invariant()

    def check_heap_invariant(self):
        '''Check the heap invariant'''
        if self.root is None:
            return True
        return self.root.check_heap_invariant()

    def depth(self):
        '''Return the depth of the treap (tree)'''
        class maxer(object):
            '''Class facilitates computing the maximum depth of all the treap (tree) branches'''
            def __init__(self, maximum=-1):
                self.max = maximum

            def feed(self, node, key, value, depth, from_left):
                # pylint: disable=R0913
                # R0913: We need a bunch of arguments
                '''Check our maximum so far against the current node - updating as needed'''
                dummy = node
                dummy = key
                dummy = value
                dummy = from_left
                if depth > self.max:
                    self.max = depth

            def result(self):
                '''Return the maximum we've found - plus one for human readability'''
                return self.max + 1

        max_obj = maxer()
        self.detailed_inorder_traversal(max_obj.feed)
        return max_obj.result()

    def _depth_and_field_width(self):
        '''Compute the depth of the tree and the maximum width within the nodes - for pretty printing'''
        class maxer(object):
            '''Class facilitates computing the max depth of the treap (tree) and max width of the nodes'''
            def __init__(self, maximum=-1):
                self.depth_max = maximum
                self.field_width_max = -1

            def feed(self, node, key, value, depth, from_left):
                '''Check our maximums so far against the current node - updating as needed'''
                # pylint: disable=R0913
                # R0913: We need a bunch of arguments
                dummy = key
                dummy = value
                dummy = from_left
                if depth > self.depth_max:
                    self.depth_max = depth
                str_node = str(node)
                len_key = len(str_node)
                if len_key > self.field_width_max:
                    self.field_width_max = len_key

            def result(self):
                '''Return the maximums we've computed'''
                return (self.depth_max + 1, self.field_width_max)

        max_obj = maxer()
        self.detailed_inorder_traversal(max_obj.feed)
        return max_obj.result()

    def __str__(self):
        '''Format a treap as a string'''
        class Desc(object):
            # pylint: disable=R0903
            # R0903: We don't need a lot of public methods
            '''Build a pretty-print string during a recursive traversal'''
            def __init__(self, pretree):
                self.tree = pretree

            def update(self, node, key, value, depth, from_left):
                '''Add a node to the tree'''
                # pylint: disable=R0913
                # R0913: We need a bunch of arguments
                dummy = key
                dummy = value
                self.tree[depth][from_left] = str(node)

        if self.root is None:
            # empty output for an empty tree
            return ''
        pretree = []
        depth, field_use_width = self._depth_and_field_width()
        field_use_width += 1
        for level in range(depth):
            string = '_' * (field_use_width - 1)
            pretree.append([string] * 2 ** level)
        desc = Desc(pretree)
        self.root.detailed_inorder_traversal(desc.update)
        result = []
        widest = 2 ** (depth - 1) * field_use_width
        for level in range(depth):
            two_level = 2 ** level
            field_avail_width = widest / two_level
            string = ''.join([center(x, field_use_width, field_avail_width) for x in desc.tree[level]])
            # this really isn't useful for more than dozen values or so, and that without priorities printed
            result.append(('%2d ' % level) + string)
        return '\n'.join(result)

    class state_class(object):
        # pylint: disable=R0903
        # R0903: We don't need a lot of public methods
        '''A state class, used for iterating over the nodes in a treap nonrecursively'''
        def __init__(self, todo, node):
            self.todo = todo
            self.node = node

        def __repr__(self):
            return '%s %s' % (self.todo, self.node)



    # These three things: keys, values, items; are a bit of a cheat.  In Python 2, they're really supposed to return lists,
    # but we return iterators like python 3.  A better implementation would check what version of python we're targetting,
    # give this behavior for python 3, and coerce the value returned to a list for python 2.
    def iterkeys(self):
        '''A macro for iterators - produces keys, values and items from almost the same code'''
        stack = [self.state_class('L', self.root)]

        while stack:
            state = stack.pop()
            if state.node is not None:
                if state.todo == 'V':
                    # yield state.node.key
                    yield state.node.key
                else:
                    if state.node.right is not None:
                        stack.append(self.state_class('R', state.node.right))
                    stack.append(self.state_class('V', state.node))
                    if state.node.left is not None:
                        stack.append(self.state_class('L', state.node.left))

    keys = iterator = __iter__ = iterkeys

    def itervalues(self):
        '''A macro for iterators - produces keys, values and items from almost the same code'''
        stack = [self.state_class('L', self.root)]

        while stack:
            state = stack.pop()
            if state.node is not None:
                if state.todo == 'V':
                    # yield state.node.key
                    yield state.node.value
                else:
                    if state.node.right is not None:
                        stack.append(self.state_class('R', state.node.right))
                    stack.append(self.state_class('V', state.node))
                    if state.node.left is not None:
                        stack.append(self.state_class('L', state.node.left))

    values = itervalues

    def iteritems(self):
        '''A macro for iterators - produces keys, values and items from almost the same code'''
        stack = [self.state_class('L', self.root)]

        while stack:
            state = stack.pop()
            if state.node is not None:
                if state.todo == 'V':
                    # yield state.node.key
                    yield state.node.key, state.node.value
                else:
                    if state.node.right is not None:
                        stack.append(self.state_class('R', state.node.right))
                    stack.append(self.state_class('V', state.node))
                    if state.node.left is not None:
                        stack.append(self.state_class('L', state.node.left))

    items = iteritems

    def reverse_iterator(self):
        '''Iterate over the nodes of the treap in reverse order'''
        stack = [self.state_class('L', self.root)]

        while stack:
            state = stack.pop()
            if state.node is not None:
                if state.todo == 'V':
                    yield state.node.key
                else:
                    if state.node.left is not None:
                        stack.append(self.state_class('L', state.node.left))
                    stack.append(self.state_class('V', state.node))
                    if state.node.right is not None:
                        stack.append(self.state_class('R', state.node.right))
