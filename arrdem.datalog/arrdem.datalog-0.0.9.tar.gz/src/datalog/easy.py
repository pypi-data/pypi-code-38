"""
Easy datalog.

Takes the core datalog engine and wraps it up so it's a little nicer to work with.

Easy because it's closer to hand, but no simpler.
"""

from typing import Sequence, Tuple

from datalog.evaluator import join as __join
from datalog.evaluator import select as __select
from datalog.reader import read
from datalog.types import Constant, Dataset, LTuple, LVar


def result(result_bindings: Tuple[Constant]):
  """Given a result tuple being (tuple, bindings) which contains a whole bunch of `Constant()` types,
  reduce the result tuple to a tuple of bare strings.


  This makes formatting and programatically consuming results less verbose - the wrapper types are
  only needed to differentiate LVars and Constants inside the engine.

  """

  result, bindings = result_bindings
  return tuple(c.value for c in result), {var.name: c.value for var, c in bindings.items()}


def q(t: Tuple[str]) -> LTuple:
  """Helper for writing terse queries.

  Takes a tuple of strings, and interprets them as a logic tuple.
  So you don't have to write the logic tuple out by hand.
  """

  def _x(s: str):
    if s[0].isupper():
      return LVar(s)
    else:
      return Constant(s)

  return tuple(_x(e) for e in t)


def select(db: Dataset, query: Tuple[str], bindings=None) -> Sequence[Tuple]:
  """Helper for interpreting tuples of strings as a query, and returning simplified results.

  Executes your query, returning matching full tuples.
  """

  return [result(t) for t in __select(db, q(query), bindings=bindings)]


def join(db: Dataset, query: Sequence[Tuple[str]], bindings=None) -> Sequence[dict]:
  """Helper for interpreting a bunch of tuples of strings as a join query, and returning simplified
results.

  Executes the query clauses as a join, returning a sequence of binding mappings such that the join constraints are simultaneously satisfied.
  """

  return [{k.name: v.value for k, v in result.items()}
          for result in __join(db, pattern, [q(c) for c in query], bindings=bindings)]
