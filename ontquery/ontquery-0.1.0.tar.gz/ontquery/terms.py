import rdflib
import sys
import copy
from itertools import chain
from urllib.parse import quote
from . import exceptions as exc, trie
from .utils import cullNone, subclasses, log
from .query import OntQuery

# FIXME ipython notebook?
# this still seems wrong, I want to know not how the file is running
# but whether the code being invoked when we call OntTerm has been
# saved to disk
interactive = getattr(sys, 'ps1', sys.flags.interactive)


class dictclass(type):

    def values(self):
        return self._dict.values()

    def __setitem__(self, key, value):
        if key not in self._dict:
            self._dict[key] = value
        elif self._dict[key] == value:
            pass
        else:
            raise KeyError(f'{key} already set to {self._dict[key]}')

    def __iter__(self):
        return iter(self._dict)

    def __getitem__(self, key):
        return self._dict[key]


class OntCuries(metaclass=dictclass):
    """ A bad implementation of a singleton dictionary based namespace.
        Probably better to use metaclass= to init this so types can be tracked.
    """
    # TODO how to set an OntCuries as the default...
    def __new__(cls, *args, **kwargs):
        #if not hasattr(cls, '_' + cls.__name__ + '_dict'):
        if not hasattr(cls, '_dict'):
            cls._dict = {}
            cls._n_to_p = {}
            cls._strie = {}
            cls._trie = {}

        for p, namespace in dict(*args, **kwargs).items():
            sn = str(namespace)
            trie.insert_trie(cls._trie, sn)
            cls._dict[p] = sn
            cls._n_to_p[sn] = p

        if args or kwargs:
            cls._pn = sorted(cls._dict.items(), key=lambda kv: len(kv[1]), reverse=True)

        return cls._dict

    @classmethod
    def new(cls):
        # FIXME yet another pattern that I don't like :/
        clsdict = dict(_dict={},
                       _n_to_p={},
                       _strie={},
                       _trie={},)

        return type('OntCuries', (OntCuries,), clsdict)

    @classmethod
    def populate(cls, graph):
        """ populate an rdflib graph with these curies """
        [graph.bind(k, v) for k, v in cls._dict.items()]

    @classmethod
    def identifier_prefixes(cls, curie_iri_prefix):
        return [cls._n_to_p[n] for n in cls.identifier_namespaces(curie_iri_prefix)]

    @classmethod
    def identifier_namespaces(cls, curie_iri_prefix):
        if ':' not in curie_iri_prefix:
            iri = cls._dict[curie_iri_prefix]
        elif '://' in curie_iri_prefix:
            iri = curie_iri_prefix
        else:
            iri = cls._dict[curie_iri_prefix.split(':', 1)[0]]

        return list(trie.get_namespaces(cls._trie, iri))

    @classmethod
    def qname(cls, iri):
        # while / is not *technically* allowed in prefix names by ttl
        # RDFa and JSON-LD do allow it, so we are going to allow it too
        # TODO cache the output mapping?
        try:
            namespace, suffix = trie.split_uri(iri)
        except ValueError as e:
            try:
                namespace = str(iri)
                prefix = cls._n_to_p[namespace]
                return prefix + ':'
            except KeyError as e:
                return iri  # can't split it then we're in trouble probably

        if namespace not in cls._strie:
            trie.insert_strie(cls._strie, cls._trie, namespace)

        if cls._strie[namespace]:
            pl_namespace = trie.get_longest_namespace(cls._strie[namespace], iri)
            if pl_namespace is not None:
                namespace = pl_namespace
                suffix = iri[len(namespace):]

        try:
            prefix = cls._n_to_p[namespace]
            return ':'.join((prefix, suffix))
        except KeyError:
            new_iri = namespace[:-1]
            sep = namespace[-1]
            qname = cls.qname(new_iri)
            # this works because when we get to an unsplitable case we simply fail
            # caching can help with performance here because common prefixes that
            # have not been shortened will show up in the cache
            return qname + sep + suffix

    @classmethod
    def _qname_old(cls, iri):
        # sort in reverse to match longest matching namespace first TODO/FIXME trie
        for prefix, namespace in cls._pn:
            if iri.startswith(namespace):
                suffix = iri[len(namespace):]
                return ':'.join((prefix, suffix))
        return iri


class Id:
    """ base for all identifiers, both local and global """


class LocalId(Id):
    """ Local identifier without the context to globalize it
        It is usually ok to skip using this class and just
        use a python string or integer (that is converted to a string)
    """


class Identifier(Id):
    """ any global identifier, manages the local/global transition """

    @classmethod
    def query_init(cls, *services, query_class=None, **kwargs):
        if query_class is None:
            query_class = OntQuery

        if not getattr(query_class, 'raw', True):
            raise TypeError('FIXME TODO only raw query classes can be used here '
                            'for non-raw initialize them directly so they won\'t bind '
                            'as the query for the instrumented form. This thing needs '
                            'a complete revamp along the lines of pathlib so that an '
                            'instrumented class can be initialized from the side')

        instrumented = cls._instrumeted_class()
        cls.query = query_class(*services, instrumented=instrumented, **kwargs)
        return cls.query

    @classmethod
    def _instrumeted_class(cls):
        if issubclass(cls, InstrumentedIdentifier): 
            return cls

        elif issubclass(cls, Identifier):
            # when initing from an uninstrumented id the last
            # instrumeted subclass prior to the next uninstrumented
            # subclass will be used, so if I subclass OntId to create
            # OrcId (an identifier for residents of Mordor) and also
            # subclass to create OntTerm, and then OrcRecord, OntId
            # will pick OntTerm when instrumenting rather than OrcRecord

            candidate = None
            for sc in subclasses(cls):
                if issubclass(sc, InstrumentedIdentifier):
                    candidate = sc
                elif issubclass(sc, Identifier):
                    break

            if candidate is None:
                raise TypeError(f'{cls} has no direct subclasses that are Instrumented')

            return candidate

        else:
            raise TypeError(f'Don\'t know what to do with a {type(cls)}')

    @classmethod
    def _uninstrumeted_class(cls):
        if issubclass(cls, InstrumentedIdentifier): 
            for candidate in cls.mro():
                if (issubclass(candidate, Identifier) and not
                    issubclass(candidate, InstrumentedIdentifier)):
                    return candidate

            raise TypeError(f'{cls} has no parent that is Uninstrumented')

        elif issubclass(cls, Identifier):
            return cls

        else:
            raise TypeError(f'Don\'t know what to do with a {type(cls)}')


class InstrumentedIdentifier(Identifier):
    """ classes that instrument a type of identifier to make it actionable """


class OntId(Identifier, str):  # TODO all terms singletons to prevent nastyness
    _namespaces = OntCuries  # overwrite when subclassing to switch curies...
    repr_arg_order = (('curie',),
                      ('prefix', 'suffix'),
                      ('iri',))
    __firsts = 'curie', 'iri'  # FIXME bad for subclassing __repr__ behavior :/
    class Error(Exception): pass
    class BadCurieError(Error): pass
    class UnknownPrefixError(Error): pass

    def __new__(cls, curie_or_iri=None, prefix=None, suffix=None, curie=None,
                iri=None, **kwargs):

        if type(curie_or_iri) == cls:
            return curie_or_iri

        if not hasattr(cls, f'_{cls.__name__}__repr_level'):
            cls.__repr_level = 0
            cls._oneshot_old_repr_args = None
            if not hasattr(cls, 'repr_args'):
                cls.repr_args = cls.repr_arg_order[0]

        iri_ps, iri_ci, iri_c = None, None, None

        if prefix is not None and suffix is not None:
            #curie_ps = ':'.join(prefix, suffix)
            iri_ps = cls._make_iri(prefix, suffix)

        if curie_or_iri is not None:
            if (curie_or_iri.startswith('http://') or
                curie_or_iri.startswith('https://') or
                curie_or_iri.startswith('file://')):
                iri_ci = curie_or_iri
                curie_ci = cls._namespaces.qname(iri_ci)
                prefix, suffix = curie_ci.split(':', 1)
            else:
                curie_ci = curie_or_iri
                try:
                    prefix, suffix = curie_ci.split(':', 1)
                except ValueError as e:
                    raise cls.BadCurieError(f'Could not split curie {curie_ci!r} '
                                            'is it actually an identifier?') from e
                iri_ci = cls._make_iri(prefix, suffix)

        if curie is not None and curie != iri:
            prefix, suffix = curie.split(':', 1)
            iri_c = cls._make_iri(prefix, suffix)

        iris = iri_ps, iri_ci, iri_c, iri
        unique_iris = set(i for i in iris if i is not None)

        if len(unique_iris) > 1:
            raise ValueError(f'All ways of constructing iris not match! {sorted(unique_iris)}')
        else:
            iri = next(iter(unique_iris))

        if iri is not None:
            # normalization step in case there is a longer prefix match
            curie_i = cls._namespaces.qname(iri)
            prefix_i, suffix_i = curie_i.split(':', 1)
            #if prefix and prefix_i != prefix:
                #print('Curie changed!', prefix + ':' + suffix, '->', curie_i)
            prefix, suffix = prefix_i, suffix_i
            if not suffix.startswith('//') and curie_i == iri:
                raise ValueError(f'You have provided a curie {curie_i} as an iri!')

        if ' ' in prefix or ' ' in suffix:
            raise cls.BadCurieError(f'{prefix}:{suffix} has an invalid charachter in it!')

        self = super().__new__(cls, iri)

        # FIXME these assignments prevent updates when OntCuries changes
        self.prefix = prefix
        self.suffix = suffix
        return self

    @property
    def namespaces(self):
        return self._namespaces()

    @namespaces.setter
    def namespaces(self, value):
        self.__class__._namespaces = value
        # TODO recompute prefix and suffix for the new namespaces for all subclasses.
        # even though this is a property

    @property
    def namespace(self):
        if self.prefix:
            return self.namespaces[self.prefix]

    @property
    def iprefix(self):
        """ alias for self.namespace """
        return self.namespace

    @property
    def curie(self):
        if self.prefix or self.suffix:
            return ':'.join((self.prefix, self.suffix))

    @property
    def iri(self):
        return str(self)  # without str we will get infinite recursion

    @classmethod
    def _make_iri(cls, prefix, suffix):
        namespaces = cls._namespaces()
        if prefix in namespaces:
            return namespaces[prefix] + suffix
        else:
            raise cls.UnknownPrefixError(f'Unknown curie prefix: {prefix} for {prefix}:{suffix}')

    @property
    def quoted(self):
        return quote(self.iri, safe=tuple())

    @property
    def asTerm(self):
        return self._instrumented_class(self)

    @classmethod
    def repr_level(cls, verbose=True):  # FIXMe naming
        if not hasattr(cls, f'_{cls.__name__}__repr_level'):
            setattr(cls, f'_{cls.__name__}__repr_level', 0)
            #cls.__repr_level = 0 # how is this different....
        current = getattr(cls, f'_{cls.__name__}__repr_level')
        nargs = len(cls.repr_arg_order)
        next = (current + 1) % nargs
        cls.repr_args = cls.repr_arg_order[next]
        if verbose:
            log.info(f'{cls.__name__} will now repr with {cls.repr_args}')
        setattr(cls, f'_{cls.__name__}__repr_level', next)

    @classmethod
    def set_next_repr(cls, *repr_args):
        cls._oneshot_old_repr_args = cls.repr_args
        cls.repr_args = repr_args

    @classmethod
    def reset_repr_args(cls):
        if cls._oneshot_old_repr_args is not None:
            cls.repr_args = cls._oneshot_old_repr_args
            cls._oneshot_old_repr_args = None

    @property
    def _repr_level(self):
        if not hasattr(self, f'_{self.__class__.__name__}__repr_level'):
            setattr(self, f'_{self.__class__.__name__}__repr_level', 0)
        current = getattr(self.__class__, f'_{cls.__class__.__name__}__repr_level')
        nargs = len(self.repr_arg_order)
        next = (current + 1) % nargs
        self.__class__.repr_args = self.repr_arg_order[next]
        log.info(f'{self.__name__} will now repr with {self.repr_args}')
        setattr(self.__class__, f'_{self.__class__.__name__}__repr_level', next)

    @property
    def _repr_include_args(self):
        first_done = False
        firsts = getattr(self.__class__, f'_{self.__class__.__name__}__firsts')
        for arg in self.__class__.repr_args:  # always use class repr args
            if not hasattr(self, arg) or getattr(self, arg) is None:  # allow repr of uninitialized classes
                continue
            is_arg = False
            if not first_done:
                if arg in firsts:
                    first_done = True
                    is_arg = True
            yield arg, is_arg

        if hasattr(self, 'validated') and not self.validated:
            yield 'validated', False

    @property
    def _repr_base(self):
        pref = self.__class__.__name__ + '('
        suf = ')'
        return pref + ', '.join(('{' + f'{kwarg}' + '}'
                                 if is_arg else
                                 f'{kwarg}={{' + f'{kwarg}' + '}')
                                for kwarg, is_arg in self._repr_include_args) + suf

    @property
    def _repr_args(self):
        return {kwarg:repr(getattr(self, kwarg)) for kwarg, p in self._repr_include_args}

    def _no__str__(self):  # don't use this -- we need sane serialization as the iri
        id_ = self.curie if hasattr(self, 'curie') else super().__repr__()
        return f"{self.__class__.__name__}('{id_}')"

    def __repr__(self):
        out = self._repr_base.format(**self._repr_args)
        self.reset_repr_args()
        return out

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls, iri=self.iri)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls, iri=self.iri)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result


class OntTerm(InstrumentedIdentifier, OntId):
    # TODO need a nice way to pass in the ontology query interface to the class at run time to enable dynamic repr if all information did not come back at the same time
    repr_arg_order = (('curie', 'label', 'synonyms', 'definition'),
                      ('curie', 'label', 'synonyms'),
                      ('curie', 'label'),
                      ('label',),
                      ('curie',),
                      ('curie', 'label', 'definition', 'iri'),
                      ('iri', 'label', 'definition', 'curie'),
                      ('iri', 'label', 'definition'),)

    _cache = {}

    __firsts = 'curie', 'iri'

    def __new__(cls, curie_or_iri=None,  # cuire_or_iri first to allow creation without keyword
                label=None,
                term=None,
                search=None,
                validated=None,
                query=None,
                **kwargs):
        kwargs['curie_or_iri'] = curie_or_iri
        kwargs['label'] = label
        kwargs['term'] = term
        kwargs['search'] = search
        kwargs['validated'] = validated
        kwargs['query'] = query
        cls._oneshot_old_repr_args = None  # FIXME why does this fail in the hasattr case? below?!
        if curie_or_iri and 'labels' in kwargs:
            raise ValueError('labels= is not a valid keyword for results not returned by a query')
        if not hasattr(cls, f'_{cls.__name__}__repr_level'):
            cls.__repr_level = 0
            if not hasattr(cls, 'repr_args'):
                cls.repr_args = cls.repr_arg_order[0]

        orig_kwargs = {k:v for k, v in kwargs.items()}

        noId = False
        if curie_or_iri is None and 'curie' not in kwargs and 'iri' not in kwargs and 'suffix' not in kwargs:
            noId = True
            nargs = cullNone(**kwargs)
            if query is not None:
                results_gen = query(**nargs)
            else:
                results_gen = cls.query(**nargs)

            results_gen = tuple(results_gen)
            if results_gen:
                if len(results_gen) <= 1:
                    kwargs.update(results_gen[0])
        else:
            results_gen = None

        try:
            self = super().__new__(cls, **kwargs)
        except StopIteration:  # no iri found
            self = str.__new__(cls, '')  # issue will be dealt with downstream

        self.orig_kwargs = orig_kwargs
        self.kwargs = kwargs

        if query is not None:
            self.query = query

        if hasattr(self.query, 'raw') and not self.query.raw:
            raise TypeError(f'{self.query} result not set to raw, avoiding infinite recursion.')

        if self.iri not in cls._cache or validated == False or 'predicates' in kwargs:  # FIXME __cache
            # FIXME if results_gen returns > 1 result this goes infinite
            self.__real_init__(validated, results_gen, noId)
            # returning without error does NOT imply validated

        return self

    def __init__(self, *args, **kwargs):
        """ do nothing """

    def __real_init__(self, validated, results_gen, noId):
        """ If we use __init__ here it has to accept args that we don't want. """

        if results_gen is None:
            extra_kwargs = {}
            if 'predicates' in self.kwargs:
                extra_kwargs['predicates'] = self.kwargs['predicates']
            # can't gurantee that all endpoints work on the expanded iri
            #print(self.iri, self.kwargs)
            results_gen = self.query(iri=self.iri, curie=self.curie, **extra_kwargs)

        i = None
        for i, result in enumerate(results_gen):
            if i > 0:
                if result.iri == old_result.iri:
                    i = 0  # if we get the same record from multiple places it is ok
                    if result.curie != old_result.curie:
                        pass  # TODO log warning
                else:
                    if i == 1:
                        log.info(repr(TermRepr(**old_result)) + '\n')

                    log.info(repr(TermRepr(**result)) + '\n')
                    continue

            if i == 0:
                old_result = result

            for keyword, value in result.items():
                # TODO open vs closed world
                orig_value = self.orig_kwargs.get(keyword, None)
                empty_iterable = hasattr(orig_value, '__iter__') and not orig_value
                if ((orig_value is not None and not empty_iterable)
                    and value is not None and orig_value != value):
                    if str(orig_value) == value:
                        pass  # rdflib.URIRef(a) != Literl(a) != a so we have to convert
                    elif (keyword == 'label' and
                          (orig_value in result['labels'] or
                           orig_value.lower() == value.lower())):
                        pass
                    elif keyword == 'predicates':
                        pass  # query will not match result
                    else:
                        self.__class__.repr_args = 'curie', keyword
                        if validated == False:
                            raise ValueError(f'Unvalidated value {keyword}={orig_value!r} '
                                             f'does not match {keyword}={result[keyword]!r}')
                        else:
                            raise ValueError(f'value {keyword}={orig_value!r} '
                                             f'does not match {keyword}={result[keyword]!r}')
                elif orig_value is None and value is None:
                    pass
                #elif value is None:  # can't error here, need to continue
                    #raise ValueError(f'Originally given {keyword}={orig_value!r} '
                                     #f'but got {keyword}=None as a result!')
                #elif orig_value is None:  # not an error
                    #raise ValueError()

                #print(keyword, value)
                if keyword not in self.__firsts:  # already managed by OntId
                    if keyword == 'source':  # FIXME the things i do in the name of documentability >_<
                        keyword = '_source'

                    setattr(self, keyword, value)  # TODO value lists...
            self.validated = True

        if i is None:
            self._source = None
            self.validated = False
            for keyword in set(keyword  # FIXME repr_arg_order should not be what is setting this?!?!
                               for keywords in self.repr_arg_order
                               for keyword in keywords
                               if keyword not in self.__firsts):
                if keyword in self.orig_kwargs:
                    value = self.orig_kwargs[keyword]
                else:
                    value = None
                setattr(self, keyword, value)
            rargs = {k:v for k, v in self.orig_kwargs.items()
                     if k not in ('validated', 'query') and v is not None}
            if 'curie_or_iri' in rargs:  # curei_or_iri not in repr_args
                rargs['curie'] = self.curie
            self.set_next_repr(*rargs)
            if not self.iri:
                for k, v in rargs.items():
                    setattr(self, k, v)
                raise exc.NotFoundError(f'No results for {self!r}')
            else:
                log.warning(repr(self) + '\n')

            return
            # TODO this needs to go in a separate place, not here
            # and it needs to be easy to take a constructed term
            # and turn it into a term request
            for service in self.query.services:
                self.termRequests = []
                # FIXME configure a single term request service
                if hasattr(service, 'termRequest'):
                    makeRequest = service.termRequest(self)
                    termRequests.append(makeRequest)

        elif i > 0:
            raise exc.ManyResultsError(f'\nQuery {self.orig_kwargs} returned more than one result. '
                                       'Please review.\n')
        elif noId and not interactive:
            self.set_next_repr('curie', 'label')
            raise exc.NoExplicitIdError('Your term does not have a valid identifier.\n'
                                        f'Please replace it with {self!r}')

    def debug(self):
        """ return debug information """
        if self._graph:
            print(self._graph.serialize(format='nifttl').decode())

    @property
    def source(self):
        """ The service that the term came from.
            It is not obvious that source is being set from QueryResult.
            I'm sure there are other issues like this due to the strange
            interaction between OntTerm and QueryResult. """

        return self._source

    @classmethod
    def search(cls, expression, prefix=None, filters=tuple(), limit=40):
        """ Something that actually sort of works """
        OntTerm = cls
        if expression is None and prefix is not None:
            # FIXME bad convention
            return sorted(qr.OntTerm
                          for qr in OntTerm.query(search=expression,
                                                  prefix=prefix, limit=limit))

        return sorted(set(next(OntTerm.query(term=s)).OntTerm
                          for qr in OntTerm.query(search=expression,
                                                  prefix=prefix, limit=limit)
                          for s in chain(OntTerm(qr.iri).synonyms, (qr.label,))
                          if all(f in s for f in filters)),
                          key=lambda t:t.label)

    def __call__(self, predicate, *predicates, depth=1, direction='OUTGOING', as_term=False):
        """ Retrieve additional metadata for the current term. If None is provided
            as the first argument the query runs against all predicates defined for
            each service. """
        single_out = not predicates and predicate is not None
        if predicate is None:
            predicates = self.query.predicates
        else:
            predicates = (predicate,) + predicates  # ensure at least one

        results_gen = self.query(iri=self, predicates=predicates, depth=depth, direction=direction)
        out = {}
        for result in results_gen:  # FIXME should only be one?!
            for k, v in result.predicates.items():
                if not isinstance(v, tuple):
                    v = v,

                if as_term:
                    v = tuple(self.__class__(v) if isinstance(v, OntId) else v for v in v)

                if k in out:
                    out[k] += v
                else:
                    out[k] = v

        if not hasattr(self, 'predicates'):
            self.predicates = {}

        self.predicates.update(out)  # FIXME klobbering issues

        if single_out:
            if out:
                p = OntId(predicate).curie  # need to normalize here since we don't above
                if p in out:  # FIXME rdflib services promiscuously returns predicates
                    return out[p]

            return tuple()  # more consistent return value so can always iterate
        else:
            return out

    @property
    def type(self):
        if not hasattr(self, '_type'):
            qr = next(self.query(self.iri))
            self._type = qr.type
            self._types = qr.types

        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def types(self):
        if not hasattr(self, '_types'):
            qr = next(self.query(self.iri))
            self._type = qr.type
            self._types = qr.types

        return self._types

    @types.setter
    def types(self, value):
        self._types = value

    def __repr__(self):  # TODO fun times here
        return super().__repr__()


class TermRepr(OntTerm):
    repr_arg_order = (('curie', 'label', 'synonyms'),)
    repr_args = repr_arg_order[0]
    _oneshot_old_repr_args = None
    __firsts = 'curie', 'iri'

    def __new__(cls, *args, **kwargs):
        iri = kwargs['iri']
        self = str.__new__(cls, iri)
        return self

    def __init__(self, *args, **kwargs):
        self.iri = kwargs['iri']
        self.curie = kwargs['curie']
        self.label = kwargs['label']

    @property
    def curie(self):
        return self._curie

    @curie.setter
    def curie(self, value):
        self._curie = value

    @property
    def iri(self):
        return self._iri

    @iri.setter
    def iri(self, value):
        self._iri = value


class OntComplete(OntTerm):
    """ EXPERIMENTAL OntTerm that populates properties from OntQuery """

    class _fakeQuery:
        def __call__(self, *args, **kwargs):
            raise NotImplementedError('Set OntComplete.query = OntQuery(...)')

        @property
        def predicates(self):
            raise NotImplementedError('Set OntComplete.query = OntQuery(...)')

    query = _fakeQuery()

    def __new__(cls, *args, **kwargs):
        for predicate in cls.query.predicates:
            p = OntId(predicate)
            name = p.suffix if p.suffix else p.prefix  # partOf:

            def _prop(self, *predicates, depth=1):
                return cls.__call__(self, *predicates, depth=depth)

            prop = property(_prop)
            setattr(cls, name, prop)

        return super().__new__(*args, **kwargs)
