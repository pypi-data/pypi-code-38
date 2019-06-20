"""
Operations for sums of rational functions and an interface to LattE's 'count --multivariate-generating-function'
"""

from __future__ import absolute_import, division
from sage.all import *
from sage.features.latte import Latte_count
from sage.modules.free_module_element import vector

from . import common

from .util import my_find_executable, TemporaryDirectory, cd, augmented_env
from .cycrat import CyclotomicRationalFunction

from .tmplist import TemporaryList

import os
import itertools

import subprocess

from .util import create_logger
from six.moves import range
logger = create_logger(__name__)

if not Latte_count().is_present():
    logger.warning('LattE/count not found. '
                'Computations of p-adic zeta functions are unavailable. '
                'You can try to install it by running "sage -i latte_int"')

def NonnegativeCompositions(n, length=None):
    # Produce all k-lists of nonnegative integers that sum up to k
    for c in Compositions(n+length, length=length):
        yield [a-1 for a in c]

def get_totally_nonperp_vector(vectors, strategy='random'):
    """Construct a vector 'w' such that w * v != 0 for all v in vectors.
    """
    vectors = list(vectors) # We want to allow generators.

    if not vectors:
        return None

    n = len(vectors[0])
    for k in (k for k in itertools.count() for _ in range((k+1) * n)):
        if strategy == 'random':
            v = random_vector(n, x=-k, y=k+2)
        elif strategy == 'moment':
            v = vector(ZZ, [1] + [k ** i for i in range(1,n)])
        else:
            raise TypeError('unknown strategy')

        if 0 in (v * w for w in vectors):
            continue
        return v

def taylor_processor_naive(new_ring, Phi, scalar, alpha, I, omega):
    k = alpha.nrows() - 1
    tau = SR.var('tau')
    y = [SR('y%d' % i) for i in range(k+1)]

    R = PolynomialRing(QQ, len(y), y)
    beta = [a * Phi for a in alpha]

    J = [i for i in range(1, k+1) if not(i in I)]

    def f(i):
        if i == 0:
            return QQ(scalar) * y[0] * exp(tau * omega[0])
        elif i in I:
            return 1/(1 - exp(tau * omega[i]))
        else:
            return 1/(1 - y[i] * exp(tau * omega[i]))

    h = prod(f(i) for i in range(k+1))

    # Get constant term of h as a Laurent series in tau.
    g = h.series(tau, 1).truncate().collect(tau).coefficient(tau, 0)
    g = g.factor() if g else g
    yield CyclotomicRationalFunction.from_split_expression(g, y, R).monomial_substitution(new_ring, beta)
    
def taylor_processor_factored(new_ring, Phi, scalar, alpha, I, omega):
    k = alpha.nrows() - 1
    tau = SR.var('tau')
    y = [SR('y%d' % i) for i in range(k+1)]

    R = PolynomialRing(QQ, len(y), y)
    beta = [a * Phi for a in alpha]
    
    ell = len(I)
    def f(i):
        if i == 0:
            return QQ(scalar) * y[0] * exp(tau * omega[0])
        elif i in I:
            return tau/(1 - exp(tau * omega[i]))
        else:
            return 1/(1 - y[i] * exp(tau * omega[i]))

    H = [f(i).series(tau, ell+1).truncate().collect(tau) for i in range(k+1)]

    for i in range(k+1):
        H[i] = [H[i].coefficient(tau, j) for j in range(ell+1)]

    r = []

    # Get coefficient of tau^ell in prod(H)

    for w in NonnegativeCompositions(ell, k+1):
        r = prod(
            CyclotomicRationalFunction.from_split_expression(H[i][w[i]], y, R).monomial_substitution(new_ring, beta)
            for i in range(k+1))
        yield r

def latteify_polyhedron(P):
    res = []
    lin = []

    for s in P.cdd_Hrepresentation().splitlines():
        s = s.strip()
        if s in ['H-representation', 'begin', 'end']:
            continue
        elif s.find('rational') != -1:
            res.append(s[:-len(' rational')])
        elif s.find('linearity') != -1:
            lin.append(s)
        else:
            res.append(s)
    return '\n'.join(res + lin) + '\n'

class SMURF(object):
    """
    Sums of MUltivariate Rational Functions.
    """

    def __init__(self, arg, base_list=None):
        # A sufficiently list-like object 'base_list' can be provided;
        # otherwise, we just use a native list.

        self.summands = [] if base_list is None else base_list
        if isinstance(arg, sage.rings.ring.CommutativeRing):
            self.ring = arg
        elif isinstance(arg, CyclotomicRationalFunction):
            self.summands.append(arg.copy())
            self.ring = arg.ring
        else: # we're expecting a non-empty iterable of CyclotomicRationalFunctions
            self.summands.extend(a.copy() for a in arg)
            self.ring = self.summands[0].ring

        if not self.__is_consistent():
            raise TypeError('These rational functions do not belong together')

    def __is_consistent(self):
        return all(self.summands[0].is_compatible_with(a)
                   for a in self.summands)

    def __iter__(self):
        return iter(self.summands)

    def __add__(self, other):
        if other == 0:
            other = SMURF(self.ring) # this allows us to use 'sum' for SMURFs

        if (not self.summands) and (not other.summands):
            if self.ring != other.ring:
                raise TypeError('Different rings')
            return SMURF(self.ring)
        return SMURF(itertools.chain(self.summands, other.summands))

    __radd__ = __add__

    def extend(self, other):
        if self.ring != other.ring:
            raise TypeError('Different rings')

        self.summands.extend(other.summands)
        if not self.__is_consistent():
            raise TypeError

    __iadd__ = extend
    
    def append(self, cr):
        self.summands.append(cr)
        if not self.__is_consistent():
            raise TypeError
        
    def __str__(self):
        return 'Sum of %d cyclotomic rational functions over %s' % (len(self.summands), self.ring.gens())

    def evaluate(self, variables=None):
        # This is included for debugging purposes!
        return sum(SR(s.evaluate(variables)) for s in self.summands)

    def monomial_substitution(self, new_ring, Phi, base_list=None, taylor_processor=None):
        """
        Perform monomial substitutions which are valid for the sum of 'self'
        but perhaps not for each summand.
        The algorithm used can be found in Lemma 2.5 and Theorem 2.6 of
        Barvinok, Woods: ``Short rational generating functions for lattice point
        problems'', JAMS (2003).
        """

        # NOTE: 
        # we only ever apply this function to sums which compute an integral.

        if taylor_processor is None:
            taylor_processor = taylor_processor_factored # taylor_processor_naive

        if not(self.summands):
            return SMURF(new_ring, base_list=base_list)

        v = get_totally_nonperp_vector(
            vector(QQ, w) for w in itertools.chain.from_iterable(
                f.exponents[1:] for f in self.summands
                )
            )

        Phi = matrix(QQ, Phi)
        L = Phi.column_space()
        Lperp = L.basis_matrix().right_kernel() 

        with TemporaryList() as res:
            for f in itertools.chain.from_iterable(s.triangulate() for s in self.summands):
                # First, try to apply the substitution directly. Only if that fails,
                # do we use the far more involved method of Barvinok & Woods.
                try:
                    res.append(f.monomial_substitution(new_ring, Phi))
                    continue
                except ZeroDivisionError:
                    pass

                # Setting: f == scalar * X^alpha[0] / prod(1 - X^alpha[i], i=1..k)
                scalar, alpha, k = f.polynomial, matrix(QQ,f.exponents), len(f.exponents)-1 # Note the final '-1'!
                if not scalar:
                    continue
                assert scalar.is_constant()  # note the use of 'triangulate' above

                omega = [v*a for a in alpha]
                I = [i for i in range(1, k+1) if alpha[i] in Lperp]
                res.extend(taylor_processor(new_ring, Phi, scalar, alpha, I, omega))

            return SMURF(new_ring, base_list=base_list) if not res else SMURF(res, base_list=base_list)

    @classmethod
    def from_polyhedron(cls, P, ring, base_list=None):
        """
        Use LattE to compute the generating function of a rational polyhedron
        as a sum of small rational functions.
        """
        from sage.misc.parser import Parser

        if P.is_empty():
            if ring.ngens() != P.ambient_dim():
                raise TypeError('Dimension mismatch')
            return cls(ring, base_list=base_list)
        elif P.is_zero():
            return cls([CyclotomicRationalFunction(ring.one())], base_list=base_list)
        elif len(P.vertices()) == 1 and (not P.rays()) and (not P.lines()):
            # For some reason, LattE doesn't produce .rat files for points.
            return cls([CyclotomicRationalFunction(ring.one(), exponents=[vector(ZZ,P.vertices()[0])])])

        hrep = 'polyhedron.hrep';
        ratfun = hrep + '.rat';

        with TemporaryDirectory() as tmpdir, cd(tmpdir):
            with open(hrep, 'wb') as f:
                f.write(latteify_polyhedron(P).encode("ascii"))

            with open(os.devnull, 'wb') as DEVNULL:
                retcode = subprocess.call([common.count,
                                           '--compute-vertex-cones=4ti2',
                                           '--triangulation=cddlib',
                                           '--multivariate-generating-function',
                                           hrep],
                                          stdout=DEVNULL, stderr=DEVNULL,
                                          env=augmented_env(common.count))
            if retcode != 0:
                raise RuntimeError('LattE failed. Make sure it has been patched in order to be compatible with Zeta.')

            K = FractionField(ring)
            Kone = K.one()
            pick_gen = {"x{}".format(i) : gen for (i, gen) in enumerate(K.gens())}
            maple_parser = Parser(make_var=pick_gen)

            def get_exponent(cycterm):
                monomial = -maple_parser.parse(cycterm) + Kone
                return (vector(monomial.numerator().exponents()[0]) -
                        vector(monomial.denominator().exponents()[0]))

            with TemporaryList() as summands, open(ratfun, 'rb') as f:
                for line in f:
                    line = line.decode("ascii")
                    line = line.replace("[", "").replace("]", "").strip()
                    if not line:
                        continue # ignore empty lines

                    numerator_line, denominator_line = line.split("/")
                    numerator = maple_parser.parse(numerator_line)

                    # denominator_line is of the form
                    #((1-x[0]*x[5])*(1-x[4])*(1-x[0]^(-1)*x[3])*(1-x[2]))
                    # So we remove the "outer" paranthesis, and split on ")*(".
                    # TODO: Find less hacky way to do this parsing.
                    denominator_line = denominator_line[1:-1]
                    if denominator_line.startswith("("):
                        denominator_line = denominator_line[1:]
                    if denominator_line.endswith(")"):
                        denominator_line = denominator_line[:-1]
                    den_list = denominator_line.split(")*(")
                    exponents = ([vector(ZZ, K.ngens())] +
                                [get_exponent(cycterm) for cycterm in den_list])

                    summands.append(CyclotomicRationalFunction.from_laurent_polynomial(
                                    numerator, ring, exponents))

                return cls(summands, base_list=base_list)
