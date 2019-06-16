# block these from running when imported by the standard unit tests
if __name__ == '__main__':
    
    import random

    import types

    class aggregation_rule(object):
        initialized = False
        def __init__(self, init_func, call_func):
            # attach the functions to this class
            self.init_func = types.MethodType(init_func, self)
            self.call_func = types.MethodType(call_func, self)
        def __call__(self, *args):
            if not self.initialized:
                self.init_func(args[0]) # initialize with just model
                self.initialized = True
            return self.call_func(*args)

    def setup(agg, m):
        agg.lst = random.sample(range(10), 7)

    def call(agg, m):
        return agg.lst


    f = aggregation_rule(setup, call)
    print f(0)

    import random

    # import types
    # class aggregation_rule(function): # not allowed
    #     initialized = False
    #     def __init__(self, init_func, call_func):
    #         # attach the functions to this class
    #         self.init_func = init_func
    #         self.call_func = call_func
    #     def __call__(self, *args):
    #         if not self.initialized:
    #             self.data = self.init_func(args[0]) # initialize with just model
    #             self.initialized = True
    #         return self.call_func(self.data, *args)

    def setup(m):
        return random.sample(range(10), 7)

    def call(data, m):
        return data

    import pickle
    from pyomo.environ import *
    m = AbstractModel()
    m.S = Set(initialize=aggregation_rule(setup, call))
    i = m.create_instance()
    print pickle.dumps(i)

    # f = aggregation_rule(setup, call)
    # print f(0)



    # this one is pretty good but doesn't work because pyomo looks at the rule and somehow
    # decides that it should call it with the index and a counter instead of
    # just the index (both are possible for indexed sets). It also can't be
    # pickled.

    import operator
    def make_iterable(item):
        """Return an iterable for the one or more items passed."""
        if isinstance(item, basestring):
            i = iter([item])
        else:
            try:
                # check if it's iterable
                i = iter(item)
            except TypeError:
                i = iter([item])
        return i


    def set_array_from_set(set_name, key):
        """ Create a rule function that creates a set array (indexed set of sets)
        from a standard flat set, using the specified key(s). Key should be a number
        or set/tuple of numbers, showing the column number(s) from the source set to use.
        (May not be usable with PHA, because the rule cannot be pickled.)
        (Actually, it looks like PHA doesn't pickle, so this may be OK.)
        """
        d = dict()
        def rule(m, *index):
            if not d:
                flat_set = getattr(m, set_name)
                key_indexes = tuple(make_iterable(key))
                val_indexes = tuple(i for i in range(flat_set.dimen) if i not in key_indexes)
                # these may or may not be fast, but it's handy that they automatically convert
                # lone keys and values to scalars.
                key_func = operator.itemgetter(*key_indexes)
                val_func = operator.itemgetter(*val_indexes)
                for item in flat_set:
                    dkey = key_func(item)
                    dval = val_func(item)
                    d.setdefault(dkey, [])
                    d[dkey].append(dval)
                initialized = True
            # pop results to save memory
            return d.pop(index)
        return rule

    # slice GEN_SPINNING_RESERVE_TYPES both ways for later use
    m.SPINNING_RESERVE_TYPES_FOR_GEN = Set(
        m.GENERATION_PROJECTS,
        rule=set_array_from_set('GEN_SPINNING_RESERVE_TYPES', 1)
    )
    m.GENS_FOR_SPINNING_RESERVE_TYPE = Set(
        m.SPINNING_RESERVE_TYPES_FROM_GENS,
        rule=set_array_from_set('GEN_SPINNING_RESERVE_TYPES', 2)
    )
