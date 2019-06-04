#!/usr/bin/env python
#
# expression.py - Parser for ParentValue expressions
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains functions for parsing conditional and logical
expressions, and the :class:`Expression` class for representing a parsed
expression.


.. autosummary::
   :nosignatures:

   Expression
   parseExpression
   variablesInExpression
   calculateExpressionEvaluationOrder


For a given variable, the ``ParentValues`` column of the variable table may
contain one or more *expressions*, which define conditions that parent
variables of the variable may meet in order for the variable value to be
replaced. This module contains logic for parsing and evaluating a single
expression - the evaluation of multiple comma-separated expressions is handled
in the :mod:`.importing` module.


An *expression* comprises one or more *conditional statements* (or
*statements* for short). A statement has the form::

    variable operator value

where:

  - ``variable`` is the ID of a parent variable of the variable in question.
    Variable IDs must be an integer preceded by the letter ``v``.
  - ``operator`` is a comparison operator (e.g. equals, greater than, etc.).
  - ``value`` is either ``'na'`` indicating missing, or a numeric value against
    which the parent variable is to be compared.


The following comparison operators are allowed (and the symbols used in a
statement can be found in the :attr:`SYMBOLS` dictionary):

 - equal to
 - not equal to
 - greater than
 - greater than or equal to
 - less than
 - less than or equal to


The *equal to* and *not equal to* operators may be used with a value of
``'na'`` to test whether the values for a variable are missing or present
respectively.


Multiple conditional statements may be combined with ``and``, ``or``, and
``not`` logical operations (specific symbols can be found in the
:attr:`SYMBOLS` dictionary), and precedence may be enforced with the use of
round brackets.
"""


import              logging
import              collections
import itertools as it
import functools as ft
import pyparsing as pp


log = logging.getLogger(__name__)


SYMBOLS = {
    'var' : 'v',
    'and' : '&&',
    'or'  : '||',
    'not' : '~',
    'eq'  : '==',
    'ne'  : '!=',
    'lt'  : '<',
    'le'  : '<=',
    'gt'  : '>',
    'ge'  : '>=',
    'na'  : 'na',
}
"""This dictionary contains the symbols for variables and operations that
may be used in expressions.
"""


class Expression(object):
    """The ``Expression`` class is a convenience class which can be used to
    parse and access an expression.
    """


    def __init__(self, expr):
        """Create an ``Expression`` object from the string ``expr``.

        :arg expr: Expression to be parsed.
        """

        self.__variables  = None
        self.__origExpr   = expr
        self.__expression = parseExpression(expr)


    def __str__(self):
        """Return the original string representation of the expression. """
        return self.__origExpr


    def __repr__(self):
        """Return the original string representation of the expression. """
        return str(self)


    @property
    def variables(self):
        """Return a list of all variables used in the expression. """

        if self.__variables is None:
            self.__variables = variablesInExpression(self.__expression)
        return self.__variables


    def evaluate(self, dtable, data):
        """Evaluates this ``Expression`` and returns the result.

        :arg dtable: The :class:`.DataTable` containing the data.

        :arg data:   Dictionary  containing ``{ variable : column_name }``
                     mappings from the variables used in the expressions to
                     columns in ``dtable``.

        :returns:    The outcome of the expression - ``True`` or ``False``.
        """
        return self.__expression(dtable, data)


def calculateExpressionEvaluationOrder(vids, exprs):
    """Identifies hierarchical relationships between variables.

    Given the variable table, identifies the hierarchical relationship order
    between all variables, and all parent variables used within their
    expressions.

    :arg vids:  Sequence of variable IDs

    :arg exprs: Sequence of parsed expression functions (as returned by
                :func:`parseExpression`), one for each variable in
                ``variables``. For each variable, there may be either one
                expression function, or a sequence of them.

    :returns:   A list of tuples, each containing:
                 - A hierarchy level
                 - A list of all variables at that level
                The list is in ascending order, by the hierarchy level
    """

    if len(vids) != len(exprs):
        raise ValueError('vids/exprs lengths don\'t match')

    # get a list of parents for each
    # var, then turn this into a dictionary
    # of { var : parents } mappings
    parents = []
    for expr in exprs:
        if not isinstance(expr, collections.Sequence):
            expr = [expr]
        parents.append(list(it.chain(*[e.variables for e in expr])))
    children = {i : list(sorted(p)) for i, p in zip(vids, parents)}

    # Make a list of all child/
    # parent variable IDs.
    childvids = vids
    allvids   = sorted(set(it.chain(vids, *parents)))

    # Then create a dictionary which will
    # store a hierarchy level for each
    # variable, where zero indicates that
    # the variable has no dependants.
    levels = collections.OrderedDict([(i, 0) for i in allvids])

    # Determine the hierarchy levels. For
    # each variable, we set the level on
    # each of its parents to one plus its
    # level. We use the seen set to keep
    # track of variables that have already
    # been visit, and thus to detect
    # circular or self-dependencies.
    def update(vid, level, seen):

        if vid in seen:
            raise ValueError('Circular dependency identified: {}'.format(vid))

        seen.add(vid)
        levels[vid] = level

        for parent in children.get(vid, set()):

            # only update parent level if it needs to
            # be updated - it may have already been
            # set by a sibling of this variable (i.e.
            # another variable at the same hierarchy
            # level as this one).
            if levels[parent] <= level:
                update(parent, level + 1, seen)

    for vid, level in levels.items():
        update(vid, level, set())

    # Now we can just sort the variables
    # by hierarchy to get the expression
    # evaluation order.
    bylevel = collections.OrderedDict()
    for vid, level in levels.items():
        if vid not in childvids:
            continue
        if level not in bylevel: bylevel[level]     = [vid]
        else:                    bylevel[level].append(vid)

    return list(sorted(bylevel.items(), key=lambda l: l[0]))


def parseExpression(expr):
    """Parses a string containing an expression.

    The expression may contain conditional statements of the form::
        variable comparison_operator value

    combined with logical expressions using symbols for ``and``, ``or``, and
    ``not``.

    The ``parseExpression`` function, given an expression string, will return
    a function that can be used to evaluate the expression. An expression
    function expects to be given two arguments:

    - A ``pandas.DataFrame`` which contains the data on all variables used
      in the expression
    - A dictionary containing ``{variable : column}`` mappings from the
      variables used in the expression to the columns of the data frame.

    An expression function will simply return ``True`` or ``False``, depending
    on the outcome of the expression.

    Expression functions have a few attributes containing metadata about the
    expression:

      - ``ftype`` contains the expression type, either ``logical_not``,
        ``logical`` (for *and*/*or* operations), or ``condition`` (for
        comparison operations)
      - ``operation`` contains the operation symbol

    Boolean *and*/*or* functions contain ``operand1`` and ``operand2``
    attributes which refer to the expression functions they will be applied
    to. Similarly, boolean *not* functions contain an ``operand`` attribute
    which refers to the expression function it will be applied to.  Comparison
    expression functions contain ``variable`` and ``value`` attributes, which
    contain the variable name and the value involved in the comparison.

    :arg expr: String containing an expression.
    :returns:  A function which can be used to evaluate the expression.
    """
    try:
        return list(makeParser().parseString(expr, parseAll=True))[0]
    except Exception as e:
        log.error('Error parsing expression "{}": {}'.format(expr, e))
        raise e


def variablesInExpression(expr):
    """Given an expression returned by :func:`parseExpression`, extracts all
    variables used in the expression.

    :arg expr: A *parsed* expression, produced by :func:`parseExpression`.
    :returns:  A set containing all of the variables that are mentioned in
               the expression.
    """

    if expr.ftype == 'condition':
        return set([expr.variable])

    elif expr.ftype == 'logical':
        variables = set()
        variables.update(variablesInExpression(expr.operand1))
        variables.update(variablesInExpression(expr.operand2))
        return variables

    elif expr.ftype == 'logical_not':
        return variablesInExpression(expr.operand)


def makeParser():
    """Generates a ``pyparsing`` parser which can be used to parse expressions.

    :returns: A ``pyparsing`` object which can parse an expression.
    """

    if getattr(makeParser, 'parser', None) is not None:
        return makeParser.parser

    CMP     = ['eq', 'ne', 'lt', 'le', 'gt', 'ge']
    CMP     = pp.oneOf([SYMBOLS[c] for c in CMP])
    EQS     = pp.oneOf([SYMBOLS[c] for c in ['eq', 'ne']])
    AND     = pp.CaselessLiteral(SYMBOLS['and'])
    OR      = pp.CaselessLiteral(SYMBOLS['or'])
    NOT     = pp.CaselessLiteral(SYMBOLS['not'])
    NA      = pp.CaselessLiteral(SYMBOLS['na'])
    NUM     = pp.pyparsing_common.number
    VAR     = (pp.CaselessLiteral(SYMBOLS['var']) +
               pp.pyparsing_common.integer).setParseAction(parseVariable)

    # a single conditional statement:
    # "variable comparison_operator value"
    NUMCOND = pp.Group(VAR + CMP + NUM).setParseAction(parseCondition)
    NACOND  = pp.Group(VAR + EQS + NA) .setParseAction(parseCondition)
    COND    = NUMCOND ^ NACOND

    # the infixNotation helper does the heavy
    # lifting for boolean operations and precedence
    parser = pp.infixNotation(
        COND,
        [(NOT, 1, pp.opAssoc.RIGHT, parseLogicalNot),
         (AND, 2, pp.opAssoc.LEFT , parseLogical),
         (OR,  2, pp.opAssoc.LEFT,  parseLogical)])

    makeParser.parser = parser
    return parser


def parseVariable(toks):
    """Called by the parser created by :func:`makeParser`. Parses a variable
    identifier, returning an integer ID.
    """
    return toks[1]


def _not(op,       *args): return ~ op(*args)              # noqa
def _and(op1, op2, *args): return op1(*args) & op2(*args)  # noqa
def _or( op1, op2, *args): return op1(*args) | op2(*args)  # noqa


def parseLogicalNot(toks):
    """Called by the parser created by :func:`makeParser`. Parses an expression
    of the form ``not expression``, where ``not`` is the corresponding symbol
    in the :attr:`OPERATIONS` dictionary, and ``expression`` is a conditional
    statement or logical expression.

    Returns a function which can be used to evaluate the expression.
    """

    operation = toks[0][0]
    operand   = toks[0][1]

    log.debug('Parsing logical: %s %s', operation, operand)

    fn           = ft.partial(_not, operand)
    fn.ftype     = 'logical_not'
    fn.operation = operation
    fn.operand   = operand

    return fn


def parseLogical(toks):
    """Called by the parser created by :func:`makeParser`. Parses an
    expression of the form ``expression1 [and|or] expression2``, where
    ``and``/``or`` are the corresponding symbols in the :attr:`OPERATIONS`
    dictionary, and ``expression1`` and ``expression2`` are conditional
    statements or logical expression.

    Returns a function which can be used to evaluate the expression.
    """

    operand1  = toks[0][0]
    operation = toks[0][1]
    operand2  = toks[0][2]

    log.debug('Parsing logical %s %s %s', operand1, operation, operand2)

    if   operation == SYMBOLS['and']: fn = _and
    elif operation == SYMBOLS['or']:  fn = _or

    fn           = ft.partial(fn, operand1, operand2)
    fn.ftype     = 'logical'
    fn.operation = operation
    fn.operand1  = operand1
    fn.operand2  = operand2

    return fn


def _isna( var, val, dt, data): return dt[:, data[var]].isna()  # noqa
def _notna(var, val, dt, data): return dt[:, data[var]].notna() # noqa
def _eq(   var, val, dt, data): return dt[:, data[var]] == val  # noqa
def _ne(   var, val, dt, data): return dt[:, data[var]] != val  # noqa
def _gt(   var, val, dt, data): return dt[:, data[var]] >  val  # noqa
def _ge(   var, val, dt, data): return dt[:, data[var]] >= val  # noqa
def _lt(   var, val, dt, data): return dt[:, data[var]] <  val  # noqa
def _le(   var, val, dt, data): return dt[:, data[var]] <= val  # noqa


def parseCondition(toks):
    """Parses a conditional statement of the form::

        variable operation value

    where:
      - ``variable`` is a variable identifier
      - ``operation`` is a comparison operation
      - ``value`` is a numeric value

    Returns a function which can be used to evaluate the conditional statement.
    """
    toks      = toks[0]
    variable  = toks[0]
    operation = toks[1]
    value     = toks[2]

    log.debug('Parsing condition: v%s %s %s', variable, operation, value)

    if   operation == SYMBOLS['eq'] and value == 'na': fn = _isna
    elif operation == SYMBOLS['ne'] and value == 'na': fn = _notna
    elif operation == SYMBOLS['eq']:                   fn = _eq
    elif operation == SYMBOLS['ne']:                   fn = _ne
    elif operation == SYMBOLS['ge']:                   fn = _ge
    elif operation == SYMBOLS['gt']:                   fn = _gt
    elif operation == SYMBOLS['le']:                   fn = _le
    elif operation == SYMBOLS['lt']:                   fn = _lt

    fn           = ft.partial(fn, variable, value)
    fn.ftype     = 'condition'
    fn.operation = operation
    fn.variable  = variable
    fn.value     = value

    return fn
