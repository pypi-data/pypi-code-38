"""
A datalog engine.
"""

from functools import reduce
from itertools import chain
import logging as log

from datalog.parser import parse
from datalog.reader import pr_str, read
from datalog.types import CachedDataset, Constant, Dataset, IndexedDataset, LVar, Rule


def match(tuple, expr, bindings=None):
  """Attempt to construct lvar bindings from expr such that tuple and expr equate.

  If the match is successful, return the binding map, otherwise return None.
  """

  bindings = bindings.copy() if bindings is not None else {}
  for a, b in zip(expr, tuple):
    # Note the lvar - lvar case is deliberately ignored.
    # This may not work out long term.
    if isinstance(a, LVar) and isinstance(b, LVar):
      continue
    elif isinstance(a, LVar) and not a in bindings and isinstance(b, Constant):
      bindings[a] = b
    elif isinstance(a, LVar) and a in bindings and bindings[a] == b:
      continue
    elif isinstance(a, LVar) and a in bindings and bindings[a] != b:
      return
    elif a != b:
      return

  return bindings


def apply_bindings(expr, bindings, strict=True):
  """Given an expr which may contain lvars, substitute its lvars for constants returning the
  simplified expr.

  """

  if strict:
    return tuple((bindings[e] if isinstance(e, LVar) else e) for e in expr)
  else:
    return tuple((bindings.get(e, e) if isinstance(e, LVar) else e) for e in expr)


def select(db: Dataset, expr, bindings=None, _recursion_guard=None, _select_guard=None):
  """Evaluate an expression in a database, lazily producing a sequence of 'matching' tuples.

  The dataset is a set of tuples and rules, and the expression is a single tuple containing lvars
  and constants. Evaluates rules and tuples, returning

  """

  def __select_tuples():
    # As an opt. support indexed scans, which is optional.
    if isinstance(db, IndexedDataset):
      iter = db.scan_index(expr)
    else:
      iter = db.tuples()

    # For all hits in the scan, check for a match
    # FIXME (arrdem 2019-06-01):
    #   Use the WALRUS OPERATOR
    for t in iter:
      _bindings = match(t, expr, bindings or {})
      if _bindings is not None:
        log.debug(f"[__select_tuples] {expr} yielded {t}\n   before: {bindings}\n   after: {_bindings}")
        yield (t, _bindings)

  def __inner_select_rules(r, cache_key, base_bindings):
    for bindings in join(db, r.pattern, r.clauses, base_bindings,
                         _recursion_guard={r, *_recursion_guard}):
      # And some fancy footwork so we return bindings in terms of THIS expr not the pattern(s)
      t = apply_bindings(r.pattern, bindings)
      if isinstance(db, CachedDataset):
        db.cache_tuple(cache_key, t)
      yield t

  def __select_rules():
    # AND now for the messy bit, we have to do rule evaluation.
    for r in db.rules():
      # HACK (arrdem 2019-05-27):
      #   To prevent infinite right-recursion, truncate on "table" so we only recur when needed.
      if r.pattern[0] == expr[0]:

        if not isinstance(db, CachedDataset) and r in _recursion_guard:
          continue

        # Establish "base" bindings from expr constants to rule lvars
        base_bindings = match(expr, r.pattern) or {}
        cache_key = (r, apply_bindings(r.pattern, base_bindings, strict=False),)

        if isinstance(db, CachedDataset):
          results = db.scan_cache(cache_key)
        else:
          results = None

        if results is None:
          results = __inner_select_rules(r, cache_key, base_bindings)

        # FIXME (arrdem 2019-06-12):
        #  It's possible that we hit an index or cache precisely and don't need to test.
        for t in results:
          p_bindings = match(t, expr)
          # It's possible that we bind a tuple, and then it doesn't match.
          if p_bindings is not None and t not in _select_guard:
            _select_guard.add(t)
            log.debug(f"[__select_rules] {pr_str(expr)} yielded {pr_str(t)}\n   before: {bindings}\n   after: {p_bindings}")
            yield (t, p_bindings,)

  if _recursion_guard is None:
    _recursion_guard = set()

  if _select_guard is None:
    _select_guard = set()

  if bindings is None:
    bindings = {}

  # Binary equality is built-in and somewhat magical.
  if expr[0] == Constant("=") and len(expr) == 3:
    e = apply_bindings(expr, bindings)
    if e[1] == e[2]:
      yield (expr, bindings)

  # Matching tuples, with or without lvars present.
  else:
    yield from __select_tuples()
    yield from __select_rules()


def join(db: Dataset, pattern, clauses, bindings, _recursion_guard=None):
  """Evaluate clauses over the dataset, joining (or antijoining) with the seed bindings.

  Yields a sequence of bindings for which all joins and antijoins were satisfied.
  """

  def __join(g, clause):
    for ts, bindings in g:
      log.debug(f"[__join] {pr_str(pattern)} {pr_str(clause)} with {bindings}")
      for t, _bindings in select(db, apply_bindings(clause, bindings, strict=False),
                                 bindings=bindings,
                                 _recursion_guard=_recursion_guard):
        _ts = ts + [t]
        _bindings = {**bindings, **_bindings}
        log.debug(f"[__joined] {pr_str(pattern)} {pr_str(clause)}\n   with {_bindings}\n   via {pr_str(_ts)}")
        yield _ts, _bindings

  def __antijoin(g, clause):
    clause = clause[1]
    for ts, bindings in g:
      log.debug(f"[__antijoin] {pr_str(pattern)} {pr_str(clause)} {bindings}")
      if not any(select(db, apply_bindings(clause, bindings, strict=False),
                        _recursion_guard=_recursion_guard)):
        log.debug(f"[__antijoin] {pr_str(pattern)} {pr_str(clause)}\n   with {bindings}\n   via {pr_str(ts)}")
        yield ts, bindings

  def _join(g, clause):
    if clause[0] == "not":
      return __antijoin(g, clause)
    else:
      return __join(g, clause)

  def _eval(init, bindings):
    for t, bindings in select(db, init,
                              bindings=bindings,
                              _recursion_guard=_recursion_guard):
      yield [t], bindings

  # Get the "first" clause which is a positive join - as these can be selects
  # and pull all antijoins so they can be sorted to the "end" as a proxy for dependency ordering
  init = None
  join_clauses = []
  antijoin_clauses = []
  for c in clauses:
    if c[0] != "not" and not init:
      init = c
    elif c[0] == "not":
      antijoin_clauses.append(c)
    else:
      join_clauses.append(c)

  # The iterator is the chained application of _join over all the clauses, seeded with the init gen.
  for ts, bindings in reduce(_join,
                             join_clauses + antijoin_clauses,
                             _eval(init, bindings)):
    log.debug(f"[join] {pr_str(pattern)} yielded {pr_str(ts)} -> {bindings}")
    yield bindings
