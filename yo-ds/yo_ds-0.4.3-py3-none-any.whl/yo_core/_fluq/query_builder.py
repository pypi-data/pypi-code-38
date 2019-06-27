from .builder_helpers import *
import itertools



class Queryable(Generic[T]):
    def __init__(self, en: Iterable[T], length: Optional[int] = None):
        self.en=en
        self.length = length

    def __iter__(self):
        for e in self.en:
            yield e

    # <editor-fold desc="core_linq">
    def select(self, selector: Callable[[T],TOut]) -> 'Queryable[TOut]':
        return Queryable(map(selector, self.en), self.length)

    def distinct(self, selector: Optional[Callable[[T],TOut]] = None) -> 'Queryable[T]':
        return Queryable(distinct(self.en, selector))

    def select_many(self, selector: Callable[[T],Iterable[TOut]]) -> 'Queryable[TOut]':
        return Queryable(itertools.chain.from_iterable(map(selector, self.en)))

    def where(self, filterSelector: Callable[[T],bool]) -> 'Queryable[T]':
        return Queryable(filter(filterSelector, self.en))

    def group_by(self, selector: Callable[[T],TKey])-> 'Queryable[Group[TKey,T]]':
        return Queryable(group_by(self.en, selector))

    def aggregate(self, aggregator: Callable[[T,T],T])->T:
        return aggregate(self.en,aggregator)

    def cast(self, _type: Type[TOut]) -> 'Queryable[TOut]':
        return Queryable(fluq_cast(self.en, _type), self.length)

    def of_type(self, _type: Type[TOut]) -> 'Queryable[TOut]':
        return Queryable(of_type(self.en, _type), None)

    def intersect(self, en2: Iterable[T])->'Queryable[T]':
        return Queryable(intersect(self.en,en2))

    def concat(self, en2: Iterable[T])->'Queryable[T]':
        return Queryable(concat(self.en, en2))

    # </editor-fold>

    # <editor-fold desc="original_asq_ordering">
    def order_by(self, selector: Callable[[T], Any]) -> 'Queryable[T]':
        return Queryable(Orderer(self.en, [(-1, selector)]), self.length)

    def order_by_descending(self, selector: Callable[[T], Any]) -> 'Queryable[T]':
        return Queryable(Orderer(self.en, [(1, selector)]), self.length)

    def then_by(self, selector: Callable[[T], Any]) -> 'Queryable[T]':
        if not isinstance(self.en, Orderer):
            raise ValueError('then_by can only be called directly after order_by or order_by_descending')
        return Queryable(Orderer(self.en, self.en._funcs + [(-1, selector)]), self.length)

    def then_by_descending(self, selector: Callable[[T], Any]) -> 'Queryable[T]':
        if not isinstance(self.en, Orderer):
            raise ValueError('then_by can only be called directly after order_by or order_by_descending')
        return Queryable(Orderer(self.en, self.en._funcs + [(1, selector)]), self.length)
    # </editor-fold>

    # <editor-fold desc="agg_methods">
    def skip(self, count) -> 'Queryable[T]':
        return Queryable(itertools.islice(self.en, count, None))

    def take(self, count) -> 'Queryable[T]':
        return Queryable(itertools.islice(self.en, count))

    def skip_while(self, condition) -> 'Queryable[T]':
        return Queryable(skip_while(self.en, condition))

    def take_while(self, condition) -> 'Queryable[T]':
        return Queryable(take_while(self.en, condition))

    def first(self)->T:
        return first(self.en, False)

    def first_or_default(self, default = None) -> T:
        return first(self.en, True, default)

    def last(self) -> T:
        return last(self.en, False)

    def last_or_default(self, default=None) -> T:
        return last(self.en, True, default)

    def single(self) -> T:
        return single(self.en, False)

    def single_or_default(self, default=None)->T:
        return single(self.en, True, default)

    def count(self)->int:
        return count(self.en)

    def sum(self)->T:
        return sum(self.en)

    def to_list(self)->List[T]:
        return list(self.en)

    def to_dictionary(self,key_selector: Optional[Callable[[T],TKey]]=None, value_selector: Optional[Callable[[T],TValue]]=None) -> Dict[TKey,TValue]:
        return to_dictionary(self.en,key_selector,value_selector)

    def to_tuple(self)->Tuple:
        return tuple(self.en)

    def to_set(self)->Set[T]:
        return to_set(self.en)

    def all(self, selector: Callable[[T],bool] = lambda z: True)->bool:
        return all(map(selector,self.en))

    def any(self, selector: Callable[[T],bool] = lambda z: True)->bool:
        return any(map(selector,self.en))

    def to_ndarray(self) -> np.ndarray:
        return to_ndarray(self.en)

    def to_series(self,
               item_to_value: Optional[Callable[[T], Any]] = None,
               item_to_index: Optional[Callable[[T], Any]] = None) -> pd.Series:
        return to_series(self.en, item_to_value, item_to_index)

    def to_dataframe(self, **kwargs) -> pd.DataFrame:
        return to_dataframe(self.en, **kwargs)

    # </editor-fold>

    # <editor-fold desc="extended_methods">
    def argmax(self, selector: Callable[[T],Any])->T:
        return arg_extremum_default(self.en,selector,True,False,None)

    def argmax_or_default(self, selector: Callable[[T],Any], default=None):
        return arg_extremum_default(self.en,selector,True,True,default)

    def argmin(self,selector: Callable[[T],Any])->T:
        return arg_extremum_default(self.en,selector,False,False,None)

    def argmin_or_default(self, selector: Callable[[T],Any], default=None):
        return arg_extremum_default(self.en, selector, False, True, default)

    def with_indices(self)-> 'Queryable[ItemWithIndex[T]]':
        return Queryable(with_indices(self.en), self.length)

    def foreach(self, action: Callable[[T],None])->None:
        foreach(self.en,action)

    def foreach_and_continue(self, action: Callable[[T],None])-> 'Queryable[T]':
        return Queryable(foreach_and_continue(self.en, action), self.length)

    def append(self,*args:T)-> 'Queryable[T]':
        return Queryable(append(self.en, args))

    def prepend(self, *args:T)-> 'Queryable[T]':
        return Queryable(prepend(self.en, args))
    # </editor-fold>


    #<editor-fold desc="Parallel">

    def fork(self, context: ForkContext, pipeline: Callable[[Any,Iterable[T]],Any]):
        return Queryable(fork(self.en,context, pipeline))

    def fire_and_forget(self, pipeline: Callable[[Iterable[T]],Any]):
        return Queryable(fork(self.en, ForkContext(None), lambda q, _ : pipeline(q)))

    def parallel_select(self, selector, workers_count=None, buffer_size=1):
        return Queryable(parallel_select(self.en, selector, workers_count, buffer_size),self.length)

    #</editor>

    #<editor-fold desc="Extension Mechanism">

    def feed(self, collector: Callable[['Queryable[T]'], TOut])->TOut:
        return collector(self)

    #</editor-fold>