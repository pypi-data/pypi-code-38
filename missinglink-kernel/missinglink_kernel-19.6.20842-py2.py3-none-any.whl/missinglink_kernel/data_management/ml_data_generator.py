# -*- coding: utf-8 -*-
class MLDataGenerator(object):
    def __init__(self, volume_id, query, data_callback, cache_directory=None, batch_size=32, use_threads=None, processes=-1, shuffle=True, cache_limit=None, drop_last=False):
        self.__volume_id = volume_id
        self.__query = query
        self.__data_callback = data_callback
        self.__batch_size = batch_size
        self.__use_threads = use_threads
        self.__processes = processes
        self.__shuffle = shuffle
        self.__cache_directory = cache_directory
        self.__cache_limit = cache_limit
        self.__config_prefix = None
        self.__drop_last = drop_last
        self.__prefetching_processes = 1
        self.__prefetching_multiprocess = False

    def set_prefetching(self, prefetching_processes, prefetching_multiprocess):
        self.__prefetching_processes = prefetching_processes
        self.__prefetching_multiprocess = prefetching_multiprocess

    def set_config_prefix(self, config_prefix):
        self.__config_prefix = config_prefix

    def __yield_single_query(self):
        yield self.__query

    @property
    def volume_id(self):
        return self.__volume_id

    @property
    def query(self):
        return self.__query

    @classmethod
    def __yield_phase_queries(cls, tree, split_visitor):
        from missinglink.legit.scam import AddPhaseFunction
        from missinglink.legit.scam import resolve_tree

        def wrap():
            for phase in ['train', 'validation', 'test']:
                if not split_visitor.has_phase(phase):
                    continue

                resolved_tree = resolve_tree(tree, AddPhaseFunction(phase))

                yield str(resolved_tree)

        return wrap

    def __get_shuffle(self, i):
        try:
            shuffle = self.__shuffle[i] if isinstance(self.__shuffle, (list, tuple)) else self.__shuffle
        except IndexError:
            shuffle = self.__shuffle[-1]

        return shuffle

    def flow(self):
        from missinglink.legit.scam import QueryParser, visit_query
        from .query_data_generator import QueryDataGeneratorFactory
        from missinglink.legit.scam import SplitVisitor, SeedVisitor

        tree = QueryParser().parse_query(self.__query)

        split_visitor = visit_query(SplitVisitor, tree)
        seed_visitor = visit_query(SeedVisitor, tree)

        factory = QueryDataGeneratorFactory(
            self.__processes, self.__use_threads,
            self.__cache_directory, self.__cache_limit, self.__data_callback,
            self.__volume_id, self.__batch_size, seed_visitor.seed, self.__drop_last)

        factory.set_config_prefix(self.__config_prefix)

        query_gen = self.__yield_phase_queries(tree, split_visitor) if getattr(split_visitor, 'has_split', True) else self.__yield_single_query

        iters = []
        for i, query in enumerate(query_gen()):
            query_iter = factory.create(query, shuffle=self.__get_shuffle(i))
            query_iter.set_prefetching(self.__prefetching_processes, self.__prefetching_multiprocess)

            iters.append(query_iter)

        return iters if len(iters) > 1 else iters[0]
