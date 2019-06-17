from anvil.server import Serializable, serializable_type

# TODO: Convert these to decorated classes once Skulpt supports class decorators.

#!defFunction(anvil.tables.query,_,pattern)!2: "Match values using a case-sensitive LIKE query, using the % wildcard character." ["like"]
class like(Serializable):
    def __init__(self, pattern):
        self.pattern = pattern
serializable_type(like)

#!defFunction(anvil.tables.query,_,pattern)!2: "Match values using a case-insensitive ILIKE query, using the % wildcard character." ["ilike"]
class ilike(Serializable):
    def __init__(self, pattern):
        self.pattern = pattern
serializable_type(ilike)

#!defFunction(anvil.tables.query,_,value)!2: "Match values greater than the provided value." ["greater_than"]
class greater_than(Serializable):
    def __init__(self, value):
        self.value = value
serializable_type(greater_than)

#!defFunction(anvil.tables.query,_,value)!2: "Match values less than the provided value." ["less_than"]
class less_than(Serializable):
    def __init__(self, value):
        self.value = value
serializable_type(less_than)

#!defFunction(anvil.tables.query,_,value)!2: "Match values greater than or equal to the provided value." ["greater_than_or_equal_to"]
class greater_than_or_equal_to(Serializable):
    def __init__(self, value):
        self.value = value
serializable_type(greater_than_or_equal_to)

#!defFunction(anvil.tables.query,_,value)!2: "Match values less than or equal to the provided value." ["less_than_or_equal_to"]
class less_than_or_equal_to(Serializable):
    def __init__(self, value):
        self.value = value
serializable_type(less_than_or_equal_to)

#!defFunction(anvil.tables.query,_,min,max,[min_inclusive=True],[max_inclusive=False])!2: "Match values between the provided min and max, optionally inclusive." ["between"]
def between(min, max, min_inclusive=True, max_inclusive=False):
    return all_of(
        greater_than_or_equal_to(min) if min_inclusive else greater_than(min),
        less_than_or_equal_to(max) if max_inclusive else less_than(max)
    )

#!defFunction(anvil.tables.query,_,query,[raw=False])!2: "Match values that match the provided full-text search query." ["full_text_match"]
class full_text_match(Serializable):
    def __init__(self, query, raw=False):
        self.query = query
        self.raw = raw
serializable_type(full_text_match)

#!defFunction(anvil.tables.query,_,*query_expressions)!2: "Match all query parameters given as arguments and keyword arguments" ["all_of"]
class all_of(Serializable):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
serializable_type(all_of)

#!defFunction(anvil.tables.query,_,*query_expressions)!2: "Match any query parameters given as arguments and keyword arguments" ["any_of"]
class any_of(Serializable):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
serializable_type(any_of)

#!defFunction(anvil.tables.query,_,*query_expressions)!2: "Match none of the query parameters given as arguments and keyword arguments" ["none_of"]
class none_of(Serializable):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
serializable_type(none_of)

#!defFunction(anvil.tables.query,_,*query_expressions)!2: "Match none of the query parameters given as arguments and keyword arguments" ["not_"]
not_ = none_of

