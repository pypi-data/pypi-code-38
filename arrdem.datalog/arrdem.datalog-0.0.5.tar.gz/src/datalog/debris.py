"""Debris."""

def shuffled(seq):
  """Because random.shuffle() is in-place >.>"""
  s = seq.copy()
  shuffle(s)
  return s


def constexpr_p(expr):
  """Predicate. True of all terms of the expr are constants."""

  return all(isinstance(e, LVar) for e in expr)
