#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Expression

"""
from ..core import AssocialTree, Tree, compute, typing, TypingError
from ..core.random import extract_rdleaf, extract_rv, random_generator, compute_leafs, replace_rdleaf
from ..core.MO import moify
from .tokens import factory
from .renders import renders


class Expression(object):

    """
    Expression class

    :example:

    >>> e = Expression.from_str("2+3*4")
    >>> e2 = e.simplify()
    >>> print(e2)
    14
    >>> for s in e2.explain():
    ...    print(s)
    2 + 3 * 4
    2 + 12
    14
    """

    RENDER = "txt"

    def __init__(self, tree, ancestor=None):
        """
        """
        self._tree = tree
        self._ancestor = ancestor

    @classmethod
    def from_str(cls, string, typing=True):
        """ Initiate the expression from a string

        :param string: String to parse to generate the Expression
        :returns: the expression

        :example:
        >>> e = Expression.from_str("2 + 3 * 4")
        >>> e
        <Exp: 2 + 3 * 4>
        >>> e = Expression.from_str("2/3")
        >>> e
        <Fraction 2 / 3>
        >>> e = Expression.from_str("2x + 1")
        >>> e
        <Linear 2x + 1>
        >>> e = Expression.from_str("2x + 1 + 5x^2")
        >>> e
        <Quadratic 2x + 1 + 5x^2>
        >>> e = Expression.from_str("2x + 1 + 5x")
        >>> e
        <Exp: 2x + 1 + 5x>

        """
        t = Tree.from_str(string)
        if typing:
            return cls._post_precessing(t)

        return cls(t)

    @classmethod
    def random(
        cls,
        template,
        conditions=[],
        rejected=[0],
        min_max=(-10, 10),
        variables_scope={},
        shuffle=False,
    ):
        """ Initiate randomly the expression

        :param template: the template of the expression
        :param conditions: conditions on randomly generate variable
        :param rejected: Values to reject for all random variables
        :param min_max: Min and max value for all random variables
        :param variables_scope: Dictionnary for each random varaibles to fic rejected and min_max
        :param shuffle: allowing to shuffle the tree
        :returns: TODO

        :example:
        >>> Expression.random("{a}/{a*k}") # doctest: +SKIP
        <Exp: -3 / -15>
        >>> Expression.random("{a}/{a*k} - 3*{b}", variables_scope={'a':{'min_max':(10, 30)}}) # doctest: +SKIP
        <Exp: 18 / 108 - 3 * 9>

        """
        rd_t = Tree.from_str(template, random=True)
        leafs = extract_rdleaf(rd_t)
        rd_varia = extract_rv(leafs)
        generated = random_generator(
            rd_varia, conditions, rejected, min_max, variables_scope
        )
        computed = compute_leafs(leafs, generated)
        t = replace_rdleaf(rd_t, computed).map_on_leaf(moify)

        if shuffle:
            raise NotImplemented("Can't suffle expression yet")

        return cls._post_precessing(t)

    @classmethod
    def _post_precessing(cls, t):
        """ Post process the tree by typing it """
        tt = cls(t)._typing()
        try:
            return factory(tt)
        except TypeError as e:
            return cls(t)

    @classmethod
    def set_render(cls, render):
        """ Define default render function 

        :param render: render function Tree -> str

        :example:
        >>> Expression.RENDER
        'txt'
        >>> e = Expression.from_str("2+3*4")
        >>> print(e)
        2 + 3 * 4
        >>> Expression.set_render('tex')
        >>> Expression.RENDER
        'tex'
        >>> print(e)
        2 + 3 \\times 4
        >>> Expression.set_render('txt')
        """
        cls.RENDER = render

    def __str__(self):
        return renders[self.RENDER](self._tree)

    def __repr__(self):
        return f"<Exp: {renders[self.RENDER](self._tree)}>"

    def _order(self, exclude_nodes=["*", "/", "**"]):
        """ Order the expression base on types

        :example:
        
        >>> e = Expression.from_str("1 + 2x + 3 + 4x")
        >>> print(e)
        1 + 2x + 3 + 4x
        >>> #print(e._order())
        1 + 3 + 2x + 4x
        >>> e = Expression.from_str("x + 6x^3 + 1 + 2x^2 + 3 + 4x^2 + 5x")
        >>> print(e._order())
        x + 5x + 6x^3 + 2x^2 + 4x^2 + 1 + 3
        """

        def signature(leaf):
            try:
                leaf.node
            except AttributeError:
                try:
                    return leaf.signature
                except AttributeError:
                    return type(leaf)
            else:
                try:
                    typed_leaf = typing(leaf.node, leaf.left_value, leaf.right_value)
                    return typed_leaf.signature
                except (AttributeError, NotImplementedError, TypingError):
                    return type(leaf)

        try:
            self._tree.node
        except AttributeError:
            return self

        organised = AssocialTree.from_any_tree(self._tree).organise_by(
            signature, recursive=True, exclude_nodes=exclude_nodes
        )
        return Expression(organised)

    def _optimize(self, exclude_nodes=["/", "**"]):
        """ Return a copy of self with an optimize tree
        
        :example:
        >>> e = Expression.from_str("2x^2+2x+3x")
        >>> print(e._tree)
        +
         > +
         | > *
         | | > 2
         | | > ^
         | | | > x
         | | | > 2
         | > *
         | | > 2
         | | > x
         > *
         | > 3
         | > x
        >>> print(e._optimize()._tree)
        +
         > *
         | > 2
         | > ^
         | | > x
         | | > 2
         > +
         | > *
         | | > 2
         | | > x
         | > *
         | | > 3
         | | > x

        """
        try:
            # TODO: need to test exclude_nodes |ven. oct.  5 08:51:02 CEST 2018
            return Expression(self._tree.balance(exclude_nodes=exclude_nodes))
        except AttributeError:
            return self

    def _typing(self):
        """ Build a copy of self with as much typing as possible
        
        :example:
        >>> e = Expression.from_str("2x", typing=False)
        >>> print(e._tree.map_on_leaf(lambda x: type(x).__name__))
        *
         > MOnumber
         > MOstr
        >>> typed_e = e._typing()
        >>> print(type(typed_e._tree))
        <class 'mapytex.calculus.core.MO.monomial.MOMonomial'>
        >>> typed_e = e._typing()
        >>> print(type(typed_e._tree))
        <class 'mapytex.calculus.core.MO.monomial.MOMonomial'>

        >>> e = Expression.from_str("2x+3+4/5", typing=False)
        >>> print(e._tree.map_on_leaf(lambda x: type(x).__name__))
        +
         > +
         | > *
         | | > MOnumber
         | | > MOstr
         | > MOnumber
         > /
         | > MOnumber
         | > MOnumber

        >>> typed_e = e._typing()
        >>> print(e._tree.map_on_leaf(lambda x: type(x).__name__))
        +
         > +
         | > *
         | | > MOnumber
         | | > MOstr
         | > MOnumber
         > /
         | > MOnumber
         | > MOnumber
        """
        try:
            return Expression(self._tree.apply(typing))
        except AttributeError:
            return self

    def _compute(self):
        """" Compute one step of self
        
        """
        try:
            return Expression(self._tree.apply_on_last_level(compute))
        except AttributeError:
            return self

    def set_ancestor(self, ancestor):
        """ Set ancestor """
        self._ancestor = ancestor

    def _simplify(self, optimize=True):
        """ Compute as much as possible the expression

        :param optimize: bool to optimize tree when it's possible
        :return: an expression

        :example:
        >>> e = Expression.from_str("2+3*4")
        >>> e
        <Exp: 2 + 3 * 4>
        >>> f = e._simplify()
        >>> f
        <Exp: 14>
        >>> f._ancestor
        <Exp: 2 + 12>
        """
        typed_exp = self._typing()

        if optimize:
            organized_exp = typed_exp._order()
            opt_exp = organized_exp._optimize()
        else:
            opt_exp = typed_exp

        comp_exp = opt_exp._compute()

        if typed_exp == comp_exp:
            typed_exp.set_ancestor(self._ancestor)
            return typed_exp
        else:
            comp_exp.set_ancestor(self)
            return comp_exp._simplify(optimize=optimize)

    def simplify(self, optimize=True):
        """ Compute as much as possible the expression

        :param optimize: bool to optimize tree when it's possible
        :return: an expression

        :example:
        >>> e = Expression.from_str("2+3*4")
        >>> e
        <Exp: 2 + 3 * 4>
        >>> f = e.simplify()
        >>> f
        <Integer 14>
        >>> f._ancestor
        <Exp: 2 + 12>
        """
        self._child = self._simplify(optimize=optimize)
        return factory(self._child, ancestor=self._child._ancestor)

    def explain(self):
        """ Yield every calculus step which have lead to self
        
        :example:
        >>> e = Expression.from_str("2+3*4")
        >>> f = e.simplify()
        >>> for s in f.explain():
        ...     print(s)
        2 + 3 * 4
        2 + 12
        14
        >>> e = Expression.from_str("1+2+3+4+5+6+7+8+9")
        >>> f = e.simplify()
        >>> for s in f.explain():
        ...     print(s)
        1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9
        3 + 7 + 11 + 7 + 17
        10 + 11 + 24
        10 + 35
        45
        >>> e = Expression.from_str("1+2+3+4+5+6+7+8+9")
        >>> f_no_balance = e.simplify(optimize=False)
        >>> for s in f_no_balance.explain():
        ...     print(s)
        1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9
        3 + 3 + 4 + 5 + 6 + 7 + 8 + 9
        6 + 4 + 5 + 6 + 7 + 8 + 9
        10 + 5 + 6 + 7 + 8 + 9
        15 + 6 + 7 + 8 + 9
        21 + 7 + 8 + 9
        28 + 8 + 9
        36 + 9
        45
        >>> e = Expression.from_str("1+2+3+4+5*6*7*8*9")
        >>> f = e.simplify()
        >>> for s in f.explain():
        ...     print(s)
        1 + 2 + 3 + 4 + 5 * 6 * 7 * 8 * 9
        3 + 7 + 30 * 7 * 72
        10 + 210 * 72
        10 + 15120
        15130

        >>> e = Expression.from_str("1+2+3+4+5*6*7*8*9")
        >>> f_no_balance = e.simplify(optimize=False)
        >>> for s in f_no_balance.explain():
        ...     print(s)
        1 + 2 + 3 + 4 + 5 * 6 * 7 * 8 * 9
        3 + 3 + 4 + 30 * 7 * 8 * 9
        6 + 4 + 210 * 8 * 9
        10 + 1680 * 9
        10 + 15120
        15130
        >>> e = Expression.from_str("1+2/3/4/5")
        >>> f = e.simplify()
        >>> for s in f.explain():
        ...     print(s)
        1 + 2 / 3 / 4 / 5
        1 + (2 / 3 * 1 / 4) / 5
        1 + (2 * 1) / (3 * 4) / 5
        1 + 2 / 12 / 5
        1 + 2 / 12 * 1 / 5
        1 + (2 * 1) / (12 * 5)
        1 + 2 / 60
        1 / 1 + 2 / 60
        (1 * 60) / (1 * 60) + 2 / 60
        60 / 60 + 2 / 60
        (60 + 2) / 60
        62 / 60
        """
        try:
            yield from self._ancestor.explain()
        except AttributeError:
            yield self
        else:
            yield self


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
