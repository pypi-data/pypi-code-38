# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Tree class

"""

from .tree_tools import to_nested_parenthesis, postfix_concatenate, show_tree
from .coroutine import coroutine, STOOOP
from .str2 import str2, rdstr2
from .operator import OPERATORS, is_operator

__all__ = ["Tree", "MutableTree"]


class Tree:

    """
    Binary tree

    This is the chosen structure to manage calculus in PyMath.

    The class is not mutable to preserve its integrity.

    """

    def __init__(self, node, left_value, right_value):
        """
        Initiate a tree with tuple (node, (left value, right value))

        :example:

        >>> t = Tree("+", 1, 2)
        >>> t.node
        '+'
        >>> t.left_value
        1
        >>> t.right_value
        2
        """
        if node is None or right_value is None:
            raise TypeError("Tree can't have an empty node or an empty right leaf")

        self.node = node

        self.left_value = left_value
        self.right_value = right_value

    @classmethod
    def from_str(cls, expression, convert_to_mo=True, random=False):
        """ Initiate a tree from an string expression

        :example:

        >>> t = Tree.from_str("2+3*4")
        >>> print(t)
        +
         > 2
         > *
         | > 3
         | > 4
        >>> t = Tree.from_str("(2+3)*4")
        >>> print(t)
        *
         > +
         | > 2
         | > 3
         > 4
        >>> t = Tree.from_str("2+3*n")
        >>> print(t)
        +
         > 2
         > *
         | > 3
         | > n
        >>> t = Tree.from_str("2+{n}*x", random=True)
        >>> print(t)
        +
         > 2
         > *
         | > {n}
         | > x


        """
        t = MutableTree.from_str(expression, convert_to_mo, random)
        return cls.from_any_tree(t)

    @classmethod
    def from_nested_parenthesis(cls, nested_parenthesis):
        """
        Initiate recursively a tree with tuple (node, (left value, right value))

        :example:

        >>> nested_par = ("+", (1, 2))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> t.node
        '+'
        >>> t.left_value
        1
        >>> t.right_value
        2
        >>> nested_par = ("+", (
        ...    ("*", (3, 4)),
        ...    2))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> t.node
        '+'
        >>> type(t.left_value)
        <class 'mapytex.calculus.core.tree.Tree'>
        >>> t.right_value
        2

        """
        try:
            nested_len = len(nested_parenthesis)
            num_len = len(nested_parenthesis[1])
        except TypeError:
            raise ValueError("Nested parenthesis are not composed of lists")

        if nested_len != 2 and num_len != 2:
            raise ValueError("Nested parenthesis don't have right shape")

        node = nested_parenthesis[0]

        try:
            left_value = cls.from_nested_parenthesis(nested_parenthesis[1][0])
        except ValueError:
            left_value = nested_parenthesis[1][0]
        try:
            right_value = cls.from_nested_parenthesis(nested_parenthesis[1][1])
        except ValueError:
            right_value = nested_parenthesis[1][1]

        return cls(node, left_value, right_value)

    @classmethod
    def from_list(cls, node, leafs):
        """ Initiate a balanced tree with one node and a list of leafs

        :param node: node for all node of the tree
        :param leafs: list of leafs

        :example:
        >>> t = Tree.from_list("+", [1, 2])
        >>> print(t)
        +
         > 1
         > 2
        >>> t = Tree.from_list("+", [1, 2, 3])
        >>> print(t)
        +
         > 1
         > +
         | > 2
         | > 3
        >>> t = Tree.from_list("+", [1, 2, 3, 4])
        >>> print(t)
        +
         > +
         | > 1
         | > 2
         > +
         | > 3
         | > 4
        >>> t = Tree.from_list("+", [1, 2])
        >>> t2 = Tree.from_list("*", [1, t])
        >>> print(t2)
        *
         > 1
         > +
         | > 1
         | > 2


        """
        len_leafs = len(leafs)
        if len_leafs < 2:
            raise ValueError(f"Not enough leafs. Need at least 2 got {len(leafs)}")
        elif len_leafs == 2:
            l_value = leafs[0]
            r_value = leafs[1]
        elif len_leafs == 3:
            l_value = leafs[0]
            r_value = cls.from_list(node, leafs[1:])
        else:
            l_value = cls.from_list(node, leafs[: len_leafs // 2])
            r_value = cls.from_list(node, leafs[len_leafs // 2 :])
        return cls(node, l_value, r_value)

    @classmethod
    def from_any_tree(cls, tree):
        """ Initial a Tree from an other type of tree (except LeafTree)

        It also work to initiate MutableTree, AssocialTree or LeafTree from
        any tree.

        :example:
        >>> t = MutableTree("*", 1, 2)
        >>> print(Tree.from_any_tree(t))
        *
         > 1
         > 2
        >>> t1 = MutableTree("*", 1, 2)
        >>> t2 = MutableTree("*", t1, 3)
        >>> print(Tree.from_any_tree(t2))
        *
         > *
         | > 1
         | > 2
         > 3
        >>> t = MutableTree("*", 1)
        >>> print(t)
        *
         > 1
         > None
        >>> Tree.from_any_tree(t)
        Traceback (most recent call last):
            ...
        TypeError: Tree can't have empty node or leaf. Got node = * and right_value = None
        >>> t = MutableTree("-", None, 1)
        >>> print(t)
        -
         > None
         > 1
        >>> print(Tree.from_any_tree(t))
        -
         > None
         > 1
        >>> tl = LeafTree("/", 1, 4)
        >>> t2 = MutableTree("*", tl, 3)
        >>> t = Tree.from_any_tree(t2)
        >>> type(t)
        <class 'mapytex.calculus.core.tree.Tree'>
        >>> type(t.left_value)
        <class 'mapytex.calculus.core.tree.LeafTree'>

        """
        node = tree.node
        left_value = tree.left_value
        right_value = tree.right_value

        if node is None or right_value is None:
            raise TypeError(
                f"Tree can't have empty node or leaf. Got node = {node} and right_value = {right_value}"
            )

        try:
            left_value.IMLEAF
        except AttributeError:
            try:
                l_value = cls.from_any_tree(left_value)
            except AttributeError:
                l_value = left_value
        else:
            l_value = left_value

        try:
            right_value.IMLEAF
        except AttributeError:
            try:
                r_value = cls.from_any_tree(right_value)
            except AttributeError:
                r_value = right_value
        else:
            r_value = right_value

        return cls(node, l_value, r_value)

    def map_on_leaf(self, function):
        """ Map on leafs a function

        :param function: take leaf value returns other value
        :returns: Tree with calculated leaf

        :example:

        >>> t = Tree.from_str("3*4+2", convert_to_mo=False)
        >>> print(t)
        +
         > *
         | > 3
         | > 4
         > 2
        >>> print(t.map_on_leaf(lambda x:2*x))
        +
         > *
         | > 6
         | > 8
         > 4

        """
        try:
            left_applied = self.left_value.map_on_leaf(function)
        except AttributeError:
            left_applied = function(self.left_value)

        try:
            right_applied = self.right_value.map_on_leaf(function)
        except AttributeError:
            right_applied = function(self.right_value)

        return Tree(self.node, left_applied, right_applied)

    def apply_on_last_level(self, function):
        """ Apply the function on last level of the tree before leaf

        :param function: (op, a, a) -> b function to apply on last level
        :returns: b if it is a 1 level Tree, Tree otherwise


        :example:

        >>> t = Tree.from_str("3*4+2")
        >>> print(t)
        +
         > *
         | > 3
         | > 4
         > 2
        >>> from .tree_tools import infix_str_concatenate
        >>> tt = t.apply_on_last_level(lambda *x: infix_str_concatenate(*x))
        >>> print(tt)
        +
         > 3 * 4
         > 2
        >>> tt = t.apply_on_last_level(lambda n, l, r: eval(str(l) + n + str(r)))
        >>> print(tt)
        +
         > 12
         > 2
        >>> ttt = tt.apply_on_last_level(lambda n, l, r: eval(str(l) + n + str(r)))
        >>> print(ttt)
        14
        """

        left_is_leaf = 0
        try:
            left_applied = self.left_value.apply_on_last_level(function)
        except AttributeError:
            left_applied = self.left_value
            left_is_leaf = 1

        right_is_leaf = 0
        try:
            right_applied = self.right_value.apply_on_last_level(function)
        except AttributeError:
            right_applied = self.right_value
            right_is_leaf = 1

        if left_is_leaf and right_is_leaf:
            try:
                return function(self.node, left_applied, right_applied)
            except NotImplementedError:
                return Tree(self.node, left_applied, right_applied)
        else:
            return Tree(self.node, left_applied, right_applied)

    def apply(self, function):
        """ Apply the function on every node of the tree

        :param function: (op, a, a) -> b
        :returns: b

        :example:

        >>> def to_nested(op, left, right):
        ...     return (op, (left, right))
        >>> nested_par = ("+", (1, 2))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> t.apply(to_nested)
        ('+', (1, 2))
        >>> assert t.apply(to_nested) == nested_par

        >>> nested_par = ("+", (
        ...    ("*", (3, 4)),
        ...    2))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> t.apply(to_nested)
        ('+', (('*', (3, 4)), 2))
        >>> assert t.apply(to_nested) == nested_par

        >>> t.apply(lambda n, l, r: eval(str(l) + n + str(r)))
        14

        """
        try:
            left_value = self.left_value.apply(function)
        except AttributeError:
            left_value = self.left_value

        try:
            right_value = self.right_value.apply(function)
        except AttributeError:
            right_value = self.right_value

        try:
            return function(self.node, left_value, right_value)
        except NotImplementedError:
            return Tree(self.node, left_value, right_value)

    def get_leafs(self, callback=lambda x: x):
        """ Generator which yield all the leaf value of the tree.
        Callback act on every leaf.

        :param callback: function on leaf

        :example:

        >>> t = Tree.from_str("3+4+5*2")
        >>> [l for l in t.get_leafs()]
        [<MOnumber 3>, <MOnumber 4>, <MOnumber 5>, <MOnumber 2>]
        >>> {type(l).__name__ for l in t.get_leafs()}
        {'MOnumber'}
        """
        try:
            yield from self.left_value.get_leafs(callback)
        except AttributeError:
            yield callback(self.left_value)
        try:
            yield from self.right_value.get_leafs(callback)
        except AttributeError:
            yield callback(self.right_value)

    def get_nodes(self, callback=lambda x: x):
        """ Generator which yield all nodes of the tree.
        Callback act on every nodes.

        :param callback: function on node

        :example:

        >>> t = Tree.from_str('3*4+2')
        >>> [l for l in t.get_nodes()]
        ['+', '*']
        >>> t = Tree.from_str('3*4+3*4')
        >>> [l for l in t.get_nodes()]
        ['+', '*', '*']
        """
        yield self.node
        try:
            yield from self.left_value.get_nodes(callback)
        except AttributeError:
            pass
        try:
            yield from self.right_value.get_nodes(callback)
        except AttributeError:
            pass

    def depth(self):
        """ Return the depth of the tree

        :example:

        >>> nested_par = ("+", (1, 2))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> t.depth()
        1
        >>> nested_par = ("+", (
        ...    ("*", (3, 4)),
        ...    2))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> t.depth()
        2
        >>> nested_par = ("+", (
        ...    ("*", (3,
        ...        ("/", (4, 4))
        ...        )),
        ...    2))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> t.depth()
        3

        """
        try:
            l_depth = self.left_value.depth()
        except AttributeError:
            l_depth = 0

        try:
            r_depth = self.right_value.depth()
        except AttributeError:
            r_depth = 0

        return 1 + max(l_depth, r_depth)

    def __str__(self):
        """ Overload str method

        :example:

        >>> nested_par = ("+", (1, 2))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> print(t)
        +
         > 1
         > 2
        >>> nested_par = ("+", (
        ...    ("*", (3, 4)),
        ...    2))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> print(t)
        +
         > *
         | > 3
         | > 4
         > 2
        >>> nested_par = ("+", (
        ...    ("*", (1, 2)),
        ...    ("*", (3, 4)),
        ...    ))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> print(t)
        +
         > *
         | > 1
         | > 2
         > *
         | > 3
         | > 4
        """
        return self.apply(show_tree)

    def to_nested_parenthesis(self):
        """ Transform the Tree into its nested parenthesis description
        :example:

        >>> nested_par = ("+", (1, 2))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> t.to_nested_parenthesis()
        ('+', (1, 2))
        >>> nested_par = ("+", (
        ...    ("*", (3, 4)),
        ...    2))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> t.to_nested_parenthesis()
        ('+', (('*', (3, 4)), 2))
        """
        return self.apply(to_nested_parenthesis)

    def to_postfix(self):
        """ Transform the Tree into postfix notation

        :example:

        >>> nested_par = ("+", (1, 2))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> t.to_postfix()
        [1, 2, '+']
        >>> nested_par = ("+", (
        ...    ("*", (3, 4)),
        ...    2))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> t.to_postfix()
        [3, 4, '*', 2, '+']
        >>> nested_par = ("+", (
        ...    ("*", (3, 4)),
        ...    ("*", (5, 6)),
        ...     ))
        >>> t = Tree.from_nested_parenthesis(nested_par)
        >>> t.to_postfix()
        [3, 4, '*', 5, 6, '*', '+']
        """
        return self.apply(postfix_concatenate)

    @property
    def short_branch(self):
        """ Get the short branch of the tree, left if same depth
        
        :return: A tree or a leaf value

        :example:
        >>> t = Tree.from_str("2+3*4")
        >>> print(t.short_branch)
        2
        >>> t = Tree.from_str("1*2*3+4*5")
        >>> print(t.short_branch)
        *
         > 4
         > 5
        >>> t = Tree.from_str("2*3+4*5")
        >>> print(t)
        +
         > *
         | > 2
         | > 3
         > *
         | > 4
         | > 5
        >>> print(t.short_branch)
        *
         > 2
         > 3
        """
        try:
            l_depth = self.left_value.depth()
        except AttributeError:
            l_depth = 0
        try:
            r_depth = self.right_value.depth()
        except AttributeError:
            r_depth = 0

        if l_depth <= r_depth:
            return self.left_value
        else:
            return self.right_value

    @property
    def long_branch(self):
        """ Get the long branch of the tree, right if same depth
        
        :return: A tree or a leaf value

        :example:
        >>> t = Tree.from_str("2+3*4")
        >>> print(t.long_branch)
        *
         > 3
         > 4
        >>> t = Tree.from_str("2*3+4*5")
        >>> print(t)
        +
         > *
         | > 2
         | > 3
         > *
         | > 4
         | > 5
        >>> print(t.long_branch)
        *
         > 4
         > 5
        >>> t = Tree.from_str("2*3+4")
        >>> print(t.long_branch)
        *
         > 2
         > 3
        """
        try:
            l_depth = self.left_value.depth()
        except AttributeError:
            l_depth = 0
        try:
            r_depth = self.right_value.depth()
        except AttributeError:
            r_depth = 0

        if l_depth <= r_depth:
            return self.right_value
        else:
            return self.left_value

    def balance(self, exclude_nodes=[]):
        """ Recursively balance the tree without permutting different nodes

        :return: balanced tree

        :example:
        >>> t = Tree.from_str("1+2+3+4+5+6+7+8+9")
        >>> print(t)
        +
         > +
         | > +
         | | > +
         | | | > +
         | | | | > +
         | | | | | > +
         | | | | | | > +
         | | | | | | | > 1
         | | | | | | | > 2
         | | | | | | > 3
         | | | | | > 4
         | | | | > 5
         | | | > 6
         | | > 7
         | > 8
         > 9
        >>> bal_t = t.balance()
        >>> print(bal_t)
        +
         > +
         | > +
         | | > +
         | | | > 1
         | | | > 2
         | | > 3
         | > +
         | | > 4
         | | > 5
         > +
         | > 6
         | > +
         | | > 7
         | | > +
         | | | > 8
         | | | > 9

        >>> t = Tree.from_str("0*1*2*3*4+5+6+7+8+9")
        >>> print(t)
        +
         > +
         | > +
         | | > +
         | | | > +
         | | | | > *
         | | | | | > *
         | | | | | | > *
         | | | | | | | > *
         | | | | | | | | > 0
         | | | | | | | | > 1
         | | | | | | | > 2
         | | | | | | > 3
         | | | | | > 4
         | | | | > 5
         | | | > 6
         | | > 7
         | > 8
         > 9
        >>> bal_t = t.balance()
        >>> print(bal_t)
        +
         > *
         | > *
         | | > *
         | | | > 0
         | | | > 1
         | | > 2
         | > *
         | | > 3
         | | > 4
         > +
         | > +
         | | > 5
         | | > 6
         | > +
         | | > 7
         | | > +
         | | | > 8
         | | | > 9

        >>> t = Tree.from_str("0+1+2+3+4+5*6*7*8*9")
        >>> print(t)
        +
         > +
         | > +
         | | > +
         | | | > +
         | | | | > 0
         | | | | > 1
         | | | > 2
         | | > 3
         | > 4
         > *
         | > *
         | | > *
         | | | > *
         | | | | > 5
         | | | | > 6
         | | | > 7
         | | > 8
         | > 9
        >>> bal_t = t.balance()
        >>> print(bal_t)
        +
         > +
         | > +
         | | > +
         | | | > 0
         | | | > 1
         | | > 2
         | > +
         | | > 3
         | | > 4
         > *
         | > *
         | | > *
         | | | > 5
         | | | > 6
         | | > 7
         | > *
         | | > 8
         | | > 9
        >>> t = Tree.from_str("0+1+2+3+4+5/6/7/8/9")
        >>> print(t)
        +
         > +
         | > +
         | | > +
         | | | > +
         | | | | > 0
         | | | | > 1
         | | | > 2
         | | > 3
         | > 4
         > /
         | > /
         | | > /
         | | | > /
         | | | | > 5
         | | | | > 6
         | | | > 7
         | | > 8
         | > 9
        >>> bal_t = t.balance(exclude_nodes=['/'])
        >>> print(bal_t)
        +
         > +
         | > +
         | | > +
         | | | > 0
         | | | > 1
         | | > 2
         | > +
         | | > 3
         | | > 4
         > /
         | > /
         | | > /
         | | | > /
         | | | | > 5
         | | | | > 6
         | | | > 7
         | | > 8
         | > 9

        """
        try:
            l_depth = self.left_value.depth()
        except AttributeError:
            l_depth = 1
        try:
            r_depth = self.right_value.depth()
        except AttributeError:
            r_depth = 1

        if (
            l_depth > r_depth + 1
            and self.node == self.left_value.node
            and self.node not in exclude_nodes
        ):
            new_left = self.left_value.long_branch
            new_right = Tree(self.node, self.left_value.short_branch, self.right_value)
            return Tree(self.node, new_left, new_right).balance(exclude_nodes)

        if (
            r_depth > l_depth + 1
            and self.node == self.right_value.node
            and self.node not in exclude_nodes
        ):
            new_right = self.right_value.long_branch
            new_left = Tree(self.node, self.left_value, self.right_value.short_branch)
            return Tree(self.node, new_left, new_right).balance(exclude_nodes)

        try:
            left_v = self.left_value.balance(exclude_nodes)
        except AttributeError:
            left_v = self.left_value
        try:
            right_v = self.right_value.balance(exclude_nodes)
        except AttributeError:
            right_v = self.right_value

        return Tree(self.node, left_v, right_v)


class MutableTree(Tree):

    """
    Mutable Tree.

    It is used to build a new tree before fixing it into a Tree

    """

    def __init__(self, node=None, left_value=None, right_value=None):
        """
        Initiate a tree with potentialy None values

        :Example:

        >>> t = MutableTree()
        >>> t.node, t.left_value, t.right_value
        (None, None, None)
        >>> t = MutableTree('*', 1)
        >>> t.node, t.left_value, t.right_value
        ('*', 1, None)
        """

        self.node = node

        self.left_value = left_value
        self.right_value = right_value

    @classmethod
    def from_str(cls, expression, convert_to_mo=True, random=False):
        """ Initiate the MutableTree

        :example:
        >>> t = MutableTree.from_str("2+3*4")
        >>> print(t)
        +
         > 2
         > *
         | > 3
         | > 4
        >>> t = MutableTree.from_str("(2+3)*4")
        >>> print(t)
        *
         > +
         | > 2
         | > 3
         > 4
        >>> t = MutableTree.from_str("4*(-2+3)")
        >>> print(t)
        *
         > 4
         > +
         | > -2
         | > 3
        >>> t = MutableTree.from_str("1+2*3+4*5")
        >>> print(t)
        +
         > +
         | > 1
         | > *
         | | > 2
         | | > 3
         > *
         | > 4
         | > 5
        >>> t = MutableTree.from_str("1+2*3*4")
        >>> print(t)
        +
         > 1
         > *
         | > *
         | | > 2
         | | > 3
         | > 4
        >>> t = MutableTree.from_str("6x + (8 + 3) * x")
        >>> print(t)
        +
         > *
         | > 6
         | > x
         > *
         | > +
         | | > 8
         | | > 3
         | > x

        """
        if random:
            str_2_mut_tree = rdstr2(cls.sink)
            return str_2_mut_tree(expression)
        else:
            str_2_mut_tree = str2(cls.sink, convert_to_mo)
            return str_2_mut_tree(expression)

    @classmethod
    @coroutine
    def sink(cls):
        """ Sink which build a build a mutabletree

        Returns the built tree when STOOOP is thrown

        :example:
        >>> sink = MutableTree.sink()
        >>> for i in ["1", "+", "2", "*", "3"]:
        ...    sink.send(i)
        >>> a = sink.throw(STOOOP)
        >>> print(a)
        +
         > 1
         > *
         | > 2
         | > 3
        >>> sink = MutableTree.sink()
        >>> for i in ["1", "*", "2", "+", "3"]:
        ...    sink.send(i)
        >>> a = sink.throw(STOOOP)
        >>> print(a)
        +
         > *
         | > 1
         | > 2
         > 3
        >>> sink = MutableTree.sink()
        >>> for i in ["-", "1", "+", "2"]:
        ...    sink.send(i)
        >>> a = sink.throw(STOOOP)
        >>> print(a)
        +
         > -
         | > None
         | > 1
         > 2
        >>> sink = MutableTree.sink()
        >>> for i in ["1", "+", "2"]:
        ...    sink.send(i)
        >>> t = sink.throw(STOOOP)
        >>> sink = MutableTree.sink()
        >>> for i in ["1", "+", t, "*", 5]:
        ...    sink.send(i)
        >>> a = sink.throw(STOOOP)
        >>> print(a)
        +
         > 1
         > *
         | > +
         | | > 1
         | | > 2
         | > 5

        """
        ans = cls()
        nested_tree = None
        try:
            while True:
                c = yield
                if c is not None:
                    if is_operator(c):
                        try:
                            ans.set_node(c)
                        except ValueError:
                            if (
                                OPERATORS[c]["precedence"]
                                > OPERATORS[ans.node]["precedence"]
                            ):
                                # the operation has to be done first
                                if nested_tree is not None:
                                    b_tree = cls(c, nested_tree, None)
                                    nested_tree = None
                                    ans.append(b_tree)
                                else:
                                    ans.append_bot(c)
                            else:
                                if nested_tree is not None:
                                    ans.append(nested_tree)
                                    nested_tree = None
                                ans.append_top(c)
                        else:
                            if nested_tree is not None:
                                ans.set_left_value(nested_tree)
                                nested_tree = None

                    else:
                        try:
                            c.node
                        except AttributeError:
                            ans.append(c)
                        else:
                            nested_tree = c
        except STOOOP:
            if nested_tree is not None:
                ans.append(nested_tree)
            yield ans

    def set_node(self, value):
        """ Set the node value.
        Once it has been changed it can't be changed again.

        :example:
        >>> t = MutableTree()
        >>> t.node
        >>> t.set_node("*")
        >>> t.node
        '*'
        >>> t.set_node("+")
        Traceback (most recent call last):
            ...
        ValueError: The node of the tree is already set
        """
        if self.node is None:
            self.node = value
        else:
            raise ValueError("The node of the tree is already set")

    def set_left_value(self, value):
        """ Set the left value.
        Once it has been changed it can't be changed again.

        :example:
        >>> t = MutableTree()
        >>> t.left_value
        >>> t.set_left_value(1)
        >>> t.left_value
        1
        >>> t.set_left_value(2)
        Traceback (most recent call last):
            ...
        ValueError: The left branch is full, use set_right_value
        """
        if self.left_value is None:
            self.left_value = value
        else:
            try:
                self.left_value.append(value)
            except AttributeError:
                raise ValueError("The left branch is full, use set_right_value")

    def set_right_value(self, value):
        """ Set the right value.
        Once it has been changed it can't be changed again.

        :example:
        >>> t = MutableTree()
        >>> t.right_value
        >>> t.set_right_value(2)
        >>> t.right_value
        2
        >>> t.set_right_value(3)
        Traceback (most recent call last):
            ...
        ValueError: The right branch is full, use append_top or append_bot
        >>> # potentielle source de problèmes??
        >>> t = MutableTree()
        >>> t.set_right_value([1])
        >>> t.right_value
        [1]
        >>> t.set_right_value(3)
        """
        if self.right_value is None:
            self.right_value = value
        else:
            try:
                self.right_value.append(value)
            except AttributeError:
                raise ValueError(
                    "The right branch is full, use append_top or append_bot"
                )

    def append(self, value):
        """ Append the value at the bottom of the tree.

        In order to enable operator with arity 1, left value can be set only
        before the node is set, assuming that those operator are placed before
        operand.

        It tries to add it on left branch first.
        If it fails, the value is appened on right branch.

        :example:
        >>> t = MutableTree()
        >>> t.append(1)
        >>> t.set_node("*")
        >>> t.append(2)
        >>> print(t)
        *
         > 1
         > 2
        >>> t.append(3)
        Traceback (most recent call last):
            ...
        ValueError: The right branch is full, use append_top or append_bot

        >>> t1 = MutableTree()
        >>> t1.append(1)
        >>> t1.set_node("*")
        >>> t2 = MutableTree()
        >>> t1.append(t2)
        >>> t1.append(2)
        >>> t2.set_node("+")
        >>> t1.append(3)
        >>> print(t1)
        *
         > 1
         > +
         | > 2
         | > 3

        >>> t1 = MutableTree()
        >>> t1.set_node("-")
        >>> t1.append(1)
        >>> print(t1)
        -
         > None
         > 1
        """
        if self.node is None:
            try:
                self.set_left_value(value)
            except ValueError:
                self.set_right_value(value)
        else:
            self.set_right_value(value)

    def append_top(self, node):
        """ Append node into the tree at the top

        :example:

        >>> t = MutableTree("*", 1, 2)
        >>> t.append_top("+")
        >>> print(t)
        +
         > *
         | > 1
         | > 2
         > None
        """

        # self_cp = MutableTree.from_any_tree(self)
        self_cp = MutableTree()
        self_cp.set_node(self.node)
        self_cp.set_left_value(self.left_value)
        self_cp.set_right_value(self.right_value)

        self.left_value, self.node, self.right_value = self_cp, node, None

    def append_bot(self, node):
        """ Append node into the tree at the bottom right_value

        :example:

        >>> t = MutableTree("*", 1, 2)
        >>> t.append_bot("+")
        >>> print(t)
        *
         > 1
         > +
         | > 2
         | > None
        >>> t.append(3)
        >>> print(t)
        *
         > 1
         > +
         | > 2
         | > 3
        >>> t.append_bot("+")
        >>> print(t)
        *
         > 1
         > +
         | > +
         | | > 2
         | | > 3
         | > None

        """

        rv = self.right_value
        try:
            if node == rv.node:
                rv.append_top(node)
            else:
                rv.append_bot(node)
        except AttributeError:
            nright_value = MutableTree()
            nright_value.set_node(node)
            nright_value.set_left_value(rv)

            self.right_value = nright_value


class LeafTree(Tree):

    """ A LeafTree is a tree which act as if it is a leaf.
    It blocks thoses methods:
     - apply
     - apply_on_last_level
    """

    IMLEAF = 1

    def apply(self, *args):
        raise AttributeError("Can't use apply on a LeafTree")

    def apply_on_last_level(self, *args):
        raise AttributeError("Can't use apply_on_last_level on a LeafTree")


class AssocialTree(Tree):

    """ Tree which concider every subtree with a node different from itself
    as a Leaf
    """

    def map_on_leaf(self, function):
        """ Map on leafs a function

        :param function: function on a single value or a tree
        :returns: Tree with calculated leaf

        :example:

        >>> t = AssocialTree.from_str("3*4+2", convert_to_mo=False)
        >>> print(t)
        +
         > *
         | > 3
         | > 4
         > 2
        >>> print(t.map_on_leaf(lambda x:10*x))
        Traceback (most recent call last):
        ...
        TypeError: unsupported operand type(s) for *: 'int' and 'AssocialTree'
        >>> def try_multiply_ten(x):
        ...    try:
        ...        return x*10
        ...    except:
        ...        return x
        >>> print(t.map_on_leaf(try_multiply_ten))
        +
         > *
         | > 3
         | > 4
         > 20

        """
        try:
            if self.left_value.node == self.node:
                left_applied = self.left_value.map_on_leaf(function)
            else:
                left_applied = function(self.left_value)
        except AttributeError:
            left_applied = function(self.left_value)

        try:
            if self.right_value.node == self.node:
                right_applied = self.right_value.map_on_leaf(function)
            else:
                right_applied = function(self.right_value)
        except AttributeError:
            right_applied = function(self.right_value)

        return Tree(self.node, left_applied, right_applied)

    def apply_on_last_level(self, function):
        raise AttributeError("apply_on_last_level not available for AssocialTree")

    def apply(self, function):
        """ Apply the function on every node of the tree

        :param function: (op, a, a) -> b
        :returns: b

        :example:

        >>> def to_nested(op, left, right):
        ...     try:
        ...         l = f"tree({left.node})"
        ...     except AttributeError:
        ...         l = left
        ...     try:
        ...         r = f"tree({right.node})"
        ...     except AttributeError:
        ...         r = right
        ...     return (op, (l, r))
        >>> t = AssocialTree.from_str("3+4+5*2")
        >>> t.apply(to_nested)
        ('+', (('+', (<MOnumber 3>, <MOnumber 4>)), 'tree(*)'))

        """
        try:
            if self.left_value.node == self.node:
                left_value = self.left_value.apply(function)
            else:
                left_value = self.left_value
        except AttributeError:
            left_value = self.left_value

        try:
            if self.right_value.node == self.node:
                right_value = self.right_value.apply(function)
            else:
                right_value = self.right_value
        except AttributeError:
            right_value = self.right_value

        return function(self.node, left_value, right_value)

    def get_leafs(self, callback=lambda x: x):
        """ Generator which yield all the leaf value of the tree.
        Callback act on every leaf.

        :param callback: function on leaf or Tree

        :example:

        >>> t = AssocialTree.from_str("3+4+5*2")
        >>> [l for l in t.get_leafs(str)]
        ['3', '4', '*\\n > 5\\n > 2']
        >>> [ l for l in t.get_leafs(lambda x:type(x).__name__) ]
        ['MOnumber', 'MOnumber', 'AssocialTree']
        """
        try:
            if self.left_value.node == self.node:
                yield from self.left_value.get_leafs(callback)
            else:
                yield callback(self.left_value)
        except AttributeError:
            yield callback(self.left_value)

        try:
            if self.right_value.node == self.node:
                yield from self.right_value.get_leafs(callback)
            else:
                yield callback(self.right_value)
        except AttributeError:
            yield callback(self.right_value)

    def balance(self):
        """ Balance the tree

        :example:
        >>> t = AssocialTree.from_str("1+2+3+4+5+6+7+8+9")
        >>> print(t)
        +
         > +
         | > +
         | | > +
         | | | > +
         | | | | > +
         | | | | | > +
         | | | | | | > +
         | | | | | | | > 1
         | | | | | | | > 2
         | | | | | | > 3
         | | | | | > 4
         | | | | > 5
         | | | > 6
         | | > 7
         | > 8
         > 9
        >>> bal_t = t.balance()
        >>> print(bal_t)
        +
         > +
         | > +
         | | > 1
         | | > 2
         | > +
         | | > 3
         | | > 4
         > +
         | > +
         | | > 5
         | | > 6
         | > +
         | | > 7
         | | > +
         | | | > 8
         | | | > 9
        >>> t = AssocialTree.from_str("1*2*3*4*5+6+7+8+9")
        >>> print(t)
        +
         > +
         | > +
         | | > +
         | | | > *
         | | | | > *
         | | | | | > *
         | | | | | | > *
         | | | | | | | > 1
         | | | | | | | > 2
         | | | | | | > 3
         | | | | | > 4
         | | | | > 5
         | | | > 6
         | | > 7
         | > 8
         > 9
        >>> bal_t = t.balance()
        >>> print(bal_t)
        +
         > +
         | > *
         | | > *
         | | | > 1
         | | | > 2
         | | > *
         | | | > 3
         | | | > *
         | | | | > 4
         | | | | > 5
         | > 6
         > +
         | > 7
         | > +
         | | > 8
         | | > 9


        :returns: Balanced Tree (not AssocialTree)

        """
        leafs = self.get_leafs()
        balanced_leafs = []
        for l in leafs:
            try:
                balanced_leafs.append(l.balance())
            except AttributeError:
                balanced_leafs.append(l)

        t = Tree.from_list(self.node, balanced_leafs)
        return t

    def organise_by(
        self, signature=lambda x: type(x), recursive=True, exclude_nodes=[]
    ):
        """ Reoganise AssocialTree base on self order and groups by signature

        :param signature: grouping function (default type)
        :param recursive: treat nested AssocialTree the same way (default True)
        :param exclude_nodes: do not organise trees with thoses nodes (default [])

        :return: an organise version of self

        :example:
        >>> t = AssocialTree.from_list('+', [3, 4.1, 'y', 55, 2.3, 'x'])
        >>> print(t)
        +
         > +
         | > 3
         | > +
         | | > 4.1
         | | > y
         > +
         | > 55
         | > +
         | | > 2.3
         | | > x
        >>> print(t.organise_by())
        +
         > +
         | > 3
         | > 55
         > +
         | > +
         | | > 4.1
         | | > 2.3
         | > +
         | | > y
         | | > x
        >>> t = AssocialTree.from_list('+', [1, 'x', 3, 'y'])
        >>> T = AssocialTree.from_list('*', [5, 'v', 6, 'w',  t])
        >>> print(T)
        *
         > *
         | > 5
         | > v
         > *
         | > 6
         | > *
         | | > w
         | | > +
         | | | > +
         | | | | > 1
         | | | | > x
         | | | > +
         | | | | > 3
         | | | | > y
        >>> print(T.organise_by())
        *
         > *
         | > 5
         | > 6
         > *
         | > *
         | | > v
         | | > w
         | > +
         | | > +
         | | | > 1
         | | | > 3
         | | > +
         | | | > x
         | | | > y
        >>> print(T.organise_by(recursive=False))
        *
         > *
         | > 5
         | > 6
         > *
         | > *
         | | > v
         | | > w
         | > +
         | | > +
         | | | > 1
         | | | > x
         | | > +
         | | | > 3
         | | | > y
        >>> print(T.organise_by(exclude_nodes=['*']))
        *
         > *
         | > 5
         | > v
         > *
         | > 6
         | > *
         | | > w
         | | > +
         | | | > +
         | | | | > 1
         | | | | > 3
         | | | > +
         | | | | > x
         | | | | > y
        >>> t = AssocialTree.from_str('1/2/3/4')
        >>> T = AssocialTree.from_list('+', [5, t])
        >>> print(T)
        +
         > 5
         > /
         | > /
         | | > /
         | | | > 1
         | | | > 2
         | | > 3
         | > 4
        >>> print(T.organise_by(exclude_nodes=["/"]))
        +
         > 5
         > /
         | > /
         | | > /
         | | | > 1
         | | | > 2
         | | > 3
         | > 4
        """
        if self.node not in exclude_nodes:
            groups = {}
            for leaf in self.get_leafs():
                if signature(leaf) in groups:
                    groups[signature(leaf)].append(leaf)
                else:
                    groups[signature(leaf)] = [leaf]

            subtrees = []
            for group in groups.values():
                try:
                    subtrees.append(Tree.from_list(self.node, group))
                except ValueError:
                    subtrees.append(*group)
            if len(subtrees) > 1:
                tree = Tree.from_list(self.node, subtrees)
            else:
                tree = subtrees[0]
        else:
            tree = self

        if recursive:

            def contaminate_organise(leaf):
                try:
                    return leaf.organise_by(signature, recursive, exclude_nodes)
                except AttributeError:
                    return leaf

            return AssocialTree.from_any_tree(tree).map_on_leaf(contaminate_organise)

        return tree


if __name__ == "__main__":
    a = MutableTree.from_str("(1+2)*3")
    print(a)

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
