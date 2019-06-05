# coding: utf-8

#-------------------------------------------------------------------------------
# Copyright (C) 2018 Maximilian Stahlberg
#
# This file is part of PICOS.
#
# PICOS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PICOS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# This file defines the string templates used to print (algebraic) expressions.
#-------------------------------------------------------------------------------

import sys
import functools

# Allow functions to modify this module directly.
glyphs = sys.modules[__name__]

# Definitions of glyph classes and the rich strings they create.
#---------------------------------------------------------------

class GlStr(str):
    """
    A string created from a glyph.

    It has an additional :attr:`glyph` field pointing to the glyph that created
    it, and a :attr:`operands` field containing the values used to create it.
    """
    def __new__(cls, string, glyph, operands):
        return str.__new__(cls, string)

    def __init__(self, string, glyph, operands):
        self.glyph = glyph
        """The glyph used to create the string."""

        self.operands = operands
        """The operands used to create the string."""

    def reglyphed(self):
        """:returns: A rebuilt version of the string using current glyphs."""
        return self.glyph(*(op.reglyphed() if isinstance(op, GlStr) else op
            for op in self.operands))

class Gl:
    """
    The basic "glyph", a wrapper for a format string that contains special
    symbols for building (algebraic) expressions.

    Sublcasses are supposed to extend formatting routines, going beyond of what
    Python string formatting is capabale of. In particular, glyphs can be used
    to craft unambiguous algebraic expressions with the minimum amount of
    parenthesis.
    """
    def __init__(self, glyph):
        self.template = glyph
        self.initial  = glyph

    def reset(self):
        self.template = self.initial

    def update(self, new):
        self.template = new.template

    def rebuild(self):
        """
        If the template was created using other glyphs, rebuild it.

        :returns: True if the template has changed.
        """
        if isinstance(self.template, GlStr):
            oldTemplate = self.template
            self.template = self.template.reglyphed()
            return self.template != oldTemplate
        else:
            return False

    def __call__(self, *args):
        return GlStr(self.template.format(*args), self, args)

class OpStr(GlStr):
    """A string created from a math operator glyph."""
    pass

class Op(Gl):
    """
    The basic math operator glyph.

    :param str glyph: A string format template denoting the symbols to be used.
    :param int order: The operator's position in the binding strength hierarchy.
        Operators with lower numbers have precedence (bind more strongly).
    :param bool assoc: If this is ``True``, then the operator is associative, so
        that parenthesis are always omitted around operands with an equal outer
        operator. Otherwise, (1) parenthesis are used around the right hand side
        operand of a binary operation of same binding strength and (2) around
        all operands of non-binary operations of same binding strength.
    :param bool closed: If ``True``, the operator already encloses the operands
        in some sort of brackets, so that no additional parenthesis are needed.
        For glyphs where only some operands are enclosed, this can be a list.
    """
    def __init__(self, glyph, order, assoc = False, closed = False):
        self.initial = (glyph, order, assoc, closed)
        self.reset()

    def reset(self):
        self.template, self.order, self.assoc, self.closed = self.initial

    def update(self, new):
        self.template = new.template
        self.order    = new.order
        self.assoc    = new.assoc
        self.closed   = new.closed

    def __call__(self, *operands):
        if self.closed is True:
            return OpStr(self.template.format(*operands), self, operands)

        placeholders = []
        for i, operand in enumerate(operands):
            if isinstance(self.closed, list) and i < len(self.closed) \
            and self.closed[i]:
                parenthesis = False
            elif not isinstance(operand, OpStr):
                parenthesis = False
            elif operand.glyph.order < self.order:
                parenthesis = False
            elif operand.glyph.order == self.order:
                if len(operands) is 2 and i == 0:
                    # By default, bind from left to right.
                    parenthesis = False
                elif self.assoc in (None, False):
                    parenthesis = True
                else:
                    parenthesis = operand.glyph is not self
            else:
                parenthesis = True

            if type(operand) is float:
                # If no format specifier was given, then integral floats would
                # be formatted with a trailing '.0', which we don't want. Note
                # that for complex numbers the default behavior is already as we
                # want it, while 'g' would omit the parenthesis that we need.
                placeholder = "{:g}"
            else:
                placeholder = "{}"

            if parenthesis:
                placeholders.append(glyphs.parenth(placeholder))
            else:
                placeholders.append(placeholder)

        return OpStr(
            self.template.format(*placeholders).format(*operands), self, operands)

class Am(Op):
    """A math atom glyph."""
    def __init__(self, glyph):
        Op.__init__(self, glyph, 0)

class Br(Op):
    """A math operator glyph with enclosing brackets."""
    def __init__(self, glyph):
        Op.__init__(self, glyph, 0, closed = True)

class Fn(Op):
    """A math operator glyph in function form."""
    def __init__(self, glyph):
        Op.__init__(self, glyph, 0, closed = True)

class Tr(Op):
    """A math glyph in superscript/trailer form."""
    def __init__(self, glyph):
        Op.__init__(self, glyph, 1)

class Rl(Op):
    """A math relation glyph."""
    def __init__(self, glyph):
        Op.__init__(self, glyph, 5, assoc = True)

# Functions that show, reset or rebuild the glyph objects.
#---------------------------------------------------------

def show(*args):
    args = list(args) + ["{}"]*4

    print("{:8} | {:3} | {:5} | {}\n{}+{}+{}+{}".format(
        "Glyph", "Pri", "Asso", "Value", "-"*9, "-"*5, "-"*7, "-"*10))

    for name in sorted(list(glyphs.__dict__.keys())):
        glyph = getattr(glyphs, name)
        if isinstance(glyph, Gl):
            order = glyph.order if hasattr(glyph, "order") else ""
            assoc = str(glyph.assoc) if hasattr(glyph, "order") else ""
            print("{:8} | {:3} | {:5} | {}".format(
                name, order, assoc, glyph(*args)))

def rebuild():
    """
    Updates glyphs that are based upon other glyphs.
    """
    for i in range(100):
        if not any(glyph.rebuild() for glyph in glyphs.__dict__.values()
                if isinstance(glyph, Gl)):
            return

    raise Exception("Maximum recursion depth for glyph rebuilding reached. "
        "There is likely a cyclic dependence between them.")

def ascii():
    """
    Let PICOS create future string representations using only ASCII characters.
    """
    for glyph in glyphs.__dict__.values():
        if isinstance(glyph, Gl):
            glyph.reset()

# Initial glyph definitions and functions that update them.
#----------------------------------------------------------

# Non-operator glyphs.
repr1    = Gl("<{}>"); """Representation glyph."""
repr2    = Gl(glyphs.repr1("{}: {}")); """Long representation glyph."""
parenth  = Gl("({})"); """Parenthesis glyph."""
sep      = Gl("{} : {}"); """Seperator glyph."""
size     = Gl("{}x{}"); """Matrix size/shape glyph."""
compose  = Gl("{}.{}"); """Function composition glyph."""
set      = Gl("{{{}}}"); """Set glyph."""
closure  = Fn("cl{}"); """Set closure glyph."""
interval = Gl("[{}]"); """Interval glyph."""
fromto   = Gl("{}..{}"); """Range glyph."""
intrange = Gl(glyphs.interval(glyphs.fromto("{}", "{}")))
"""Integer range glyph."""
forall   = Gl("{} f.a. {}"); """Universal quantification glyph."""

# Atomic glyphs.
idmatrix = Am("I"); """Identity matrix glyph."""
lambda_  = Am("lambda"); """Lambda symbol glyph."""

# Bracketed glyphs.
matrix   = Br("[{}]"); """Matrix glyph."""
dotp     = Br("<{}, {}>"); """Scalar product glyph."""
abs      = Br("|{}|"); """Absolute value glyph."""
norm     = Br("||{}||"); """Norm glyph."""

# Special norms.
pnorm    = Op(Gl("{}_{}")(glyphs.norm("{}"), "{}"), 1, closed = [True, False])
"""p-Norm glyph."""
pqnorm   = Op(Gl("{}_{},{}")(glyphs.norm("{}"), "{}", "{}"), 1,
    closed = [True, False, False]); """pq-Norm glyph."""

# Function glyphs.
sum      = Fn("sum({})");   """Summation glyph."""
max      = Fn("max({})");   """Maximum glyph."""
min      = Fn("min({})");   """Minimum glyph."""
exp      = Fn("exp({})");   """Exponentiation glyph."""
log      = Fn("log({})");   """Logarithm glyph."""
trace    = Fn("trace({})"); """Matrix trace glyph."""
diag     = Fn("diag({})");  """Diagonal vector glyph."""
Diag     = Fn("Diag({})");  """Diagonal matrix glyph."""
det      = Fn("det({})");   """Determinant glyph."""

# Semi-closed glyphs.
ptrace   = Op("trace_{}({})", 0, closed = [False, True])
"""Matrix p-Trace glyph."""
slice    = Op("{}[{}]", 0, closed = [False, True])
"""Expression slicing glyph."""

# Trailer glyphs.
power    = Tr("{}^{}"); """Power glyph."""
cubed    = Tr(glyphs.power("{}", "3")); """Cubed value glyph."""
squared  = Tr(glyphs.power("{}", "2")); """Squared value glyph."""
transp   = Tr("{}.T"); """Matrix transposition glyph."""
ptransp  = Tr("{}.Tx"); """Matrix partial transposition glyph."""
htransp  = Tr("{}.H"); """Matrix hermitian transposition glyph."""
conj     = Tr("{}.conj"); """Complex conugate glyph."""

# Other operator glyphs.
add      = Op("{} + {}", 3, assoc = True ); """Addition glyph."""
sub      = Op("{} - {}", 3, assoc = False); """Substraction glyph."""
hadamard = Op("{}(o){}", 2, assoc = True ); """Hadamard product glyph."""
kron     = Op("{}(x){}", 2, assoc = True ); """Kronecker product glyph."""
mul      = Op("{}*{}",   2, assoc = True ); """Multiplication glyph."""
div      = Op("{}/{}",   2, assoc = False); """Division glyph."""
neg      = Op("-{}",     1.5);              """Negation glyph."""

# Concatenation glyphs.
horicat  = Op("{}, {}", 4, assoc = True); """Horizontal concatenation glyph."""
vertcat  = Op("{}; {}", 4.5, assoc = True); """Vertical concatenation glyph."""

# Relation glyphs.
element  = Rl("{} in {}"); """Set element glyph."""
eq       = Rl("{} = {}");  """Equality glyph."""
ge       = Rl("{} >= {}"); """Greater or equal glyph."""
gt       = Rl("{} > {}");  """Greater than glyph."""
le       = Rl("{} <= {}"); """Lesser or equal glyph."""
lt       = Rl("{} < {}");  """Lesser than glyph."""
psdge    = Rl("{} >> {}"); """Lesser or equal w.r.t. the p.s.d. cone glyph."""
psdle    = Rl("{} << {}"); """Greater or equal w.r.t. the p.s.d. cone glyph."""

def latin1(rebuildDerivedGlyphs = True):
    """
    Let PICOS create future string representations using ISO 8859-1 characters.
    """
    # Reset to ASCII first.
    ascii()

    # Update glyphs with only template changes.
    glyphs.compose.template  = "{}°{}"
    glyphs.cubed.template    = "{}³"
    glyphs.hadamard.template = "{}(·){}"
    glyphs.kron.template     = "{}(×){}"
    glyphs.mul.template      = "{}·{}"
    glyphs.squared.template  = "{}²"
    glyphs.psdge.template    = "{} » {}"
    glyphs.psdle.template    = "{} « {}"
    glyphs.size.template     = "{}×{}"

    # Update all derived glyphs.
    if rebuildDerivedGlyphs:
        rebuild()

def unicode(rebuildDerivedGlyphs = True):
    """
    Let PICOS create future string representations using unicode characters.
    """
    # Reset to LATIN-1 first.
    latin1(rebuildDerivedGlyphs = False)

    # Update glyphs with only template changes.
    glyphs.compose.template  = "{}∘{}"
    glyphs.dotp.template     = "⟨{}, {}⟩"
    glyphs.element.template  = "{} ∈ {}"
    glyphs.forall.template   = "{} ∀ {}"
    glyphs.fromto.template   = "{}…{}"
    glyphs.ge.template       = "{} ≥ {}"
    glyphs.hadamard.template = "{}⊙{}"
    glyphs.htransp.template  = "{}ᴴ"
    glyphs.kron.template     = "{}⊗{}"
    glyphs.lambda_.template  = "λ"
    glyphs.le.template       = "{} ≤ {}"
    glyphs.norm.template     = "‖{}‖"
    glyphs.psdge.template    = "{} ≽ {}"
    glyphs.psdle.template    = "{} ≼ {}"
    glyphs.sum.template      = "∑({})"
    glyphs.transp.template   = "{}ᵀ"

    # Update all derived glyphs.
    if rebuildDerivedGlyphs:
        rebuild()

# Default to unicode glyphs.
default = unicode
default()

# Helper functions that mimic or create additional glyphs.
#---------------------------------------------------------

def scalar(value):
    """
    This function mimics an operator glyph, but it returns a normal string (as
    opposed to an :class:`OpStr`).

    This is not realized as an atomic operator glyph to not increase the
    recursion depth of :func:`is_negated` and :func:`unnegate` unnecessarily.

    **Example**

    >>> from picos.glyphs import scalar
    >>> str(1.0)
    '1.0'
    >>> scalar(1.0)
    '1'
    """
    return ("{:g}" if type(value) is float else "{}").format(value)

def makeFunction(*names):
    """
    Creates an ad-hoc composite function glyphs.

    **Example**

    >>> from picos.glyphs import makeFunction
    >>> makeFunction("log", "sum", "exp")("x")
    'log∘sum∘exp(x)'
    """
    return Fn("{}({{}})".format(functools.reduce(glyphs.compose, names)))

# Helper functions that make context-sensitive use of glyphs.
#------------------------------------------------------------

# A sequence of unary operator glyphs for which we can factor out negation.
CAN_FACTOR_OUT_NEGATION = (
    glyphs.matrix,
    glyphs.sum,
    glyphs.trace,
    glyphs.diag,
    glyphs.Diag
)

def is_negated(value):
    """
    Checks if a value can be unnegated by :func:`unnegate`.
    """
    if isinstance(value, OpStr) and value.glyph in CAN_FACTOR_OUT_NEGATION:
        return is_negated(value.operands[0])
    elif isinstance(value, OpStr) and value.glyph is glyphs.neg:
        return True
    elif type(value) is str:
        try:
            return float(value) < 0
        except ValueError:
            return False
    elif type(value) in (int, float):
        return value < 0
    else:
        return False

def unnegate(value):
    """
    Unnegates a value in a sensible way, more precisely by recursing through
    a sequence of glyphs used to create the value and for which we can factor
    out negation, and negating the underlaying (numeric or string) value.

    :raises ValueError: When ``is_negated(value)`` returns ``False``.
    """
    if isinstance(value, OpStr) and value.glyph in CAN_FACTOR_OUT_NEGATION:
        return value.glyph(unnegate(value.operands[0]))
    elif isinstance(value, OpStr) and value.glyph is glyphs.neg:
        return value.operands[0]
    elif type(value) is str:
        # We raise any conversion error, because is_negated returns False.
        return "{:g}".format(-float(value))
    elif type(value) in (int, float):
        return -value
    else:
        raise ValueError("The value to recursively unnegate is not negated in a"
            "supported manner.")

def cleverNeg(value):
    """
    A wrapper around :attr:`neg` that resorts to unnegating an already
    negated value.

    **Example**

    >>> from picos.glyphs import neg, cleverNeg, matrix
    >>> neg("x")
    '-x'
    >>> neg(neg("x"))
    '-(-x)'
    >>> cleverNeg(neg("x"))
    'x'
    >>> neg(matrix(-1))
    '-[-1]'
    >>> cleverNeg(matrix(-1))
    '[1]'
    """
    if is_negated(value):
        return unnegate(value)
    else:
        return glyphs.neg(value)

def cleverAdd(left, right):
    """
    A wrapper around :attr:`add` that resorts to :attr:`sub` if
    the second operand was created by :attr:`neg` or is a negative
    number (string). In both cases the second operand is adjusted accordingly.

    **Example**

    >>> from picos.glyphs import neg, add, cleverAdd, matrix
    >>> add("x", neg("y"))
    'x + -y'
    >>> cleverAdd("x", neg("y"))
    'x - y'
    >>> add("X", matrix(neg("y")))
    'X + [-y]'
    >>> cleverAdd("X", matrix(neg("y")))
    'X - [y]'
    >>> cleverAdd("X", matrix(-1.5))
    'X - [1.5]'
    """
    if is_negated(right):
        return glyphs.sub(left, unnegate(right))
    else:
        return glyphs.add(left, right)

def cleverSub(left, right):
    """
    A wrapper around :attr:`sub` that resorts to :attr:`add` if
    the second operand was created by :attr:`neg` or is a negative
    number(string). In both cases the second operand is adjusted accordingly.

    **Example**

    >>> from picos.glyphs import neg, sub, cleverSub, matrix
    >>> sub("x", neg("y"))
    'x - -y'
    >>> cleverSub("x", neg("y"))
    'x + y'
    >>> sub("X", matrix(neg("y")))
    'X - [-y]'
    >>> cleverSub("X", matrix(neg("y")))
    'X + [y]'
    >>> cleverSub("X", matrix(-1.5))
    'X + [1.5]'
    """
    if is_negated(right):
        return glyphs.add(left, unnegate(right))
    else:
        return glyphs.sub(left, right)

def matrixCat(left, right, horizontal = True):
    """
    A clever wrapper around :attr:`matrix`, :attr:`horicat` and
    :attr:`vertcat`.

    **Example**

    >>> from picos.glyphs import matrixCat
    >>> Z = matrixCat("X", "Y")
    >>> Z
    '[X, Y]'
    >>> matrixCat(Z, Z)
    '[X, Y, X, Y]'
    >>> matrixCat(Z, Z, horizontal = False)
    '[X, Y; X, Y]'
    """
    if isinstance(left, OpStr) and left.glyph is glyphs.matrix:
        left = left.operands[0]

    if isinstance(right, OpStr) and right.glyph is glyphs.matrix:
        right = right.operands[0]

    catGlyph = glyphs.horicat if horizontal else glyphs.vertcat

    return glyphs.matrix(catGlyph(left, right))

def rowVectorize(*entries):
    return functools.reduce(matrixCat, entries)

def colVectorize(*entries):
    return functools.reduce(lambda l,r: matrixCat(l, r, False), entries)
