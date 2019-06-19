import itertools
import random
import sys
from functools import reduce
from typing import Iterable
from typing import Optional
from typing import Sequence
from typing import TypeVar

from putput.logger import get_logger

T = TypeVar('T')

class ComboOptions:
    """Options for join_combo via random sampling.

    Attributes:
        max_sample_size: Ceiling for number of components to sample.

        with_replacement: Option to include duplicates when randomly sampling. If True,
            will sample max_sample_size. If False, will sample up to 'max_sample_size'
            unique combinations.

    Raises:
        ValueError: If max_sample_size <= 0.
    """
    def __init__(self, *, max_sample_size: int, with_replacement: bool) -> None:
        if max_sample_size <= 0:
            raise ValueError('max_sample_size = {}, but needs to be > 0'.format(max_sample_size))
        self._max_sample_size = max_sample_size
        self._with_replacement = with_replacement

    @property
    def max_sample_size(self) -> int:
        """Ceiling for number of components to sample."""
        return self._max_sample_size

    @property
    def with_replacement(self) -> bool:
        """Option to include duplicates when randomly sampling."""
        return self._with_replacement

def join_combo(combo: Sequence[Sequence[T]], *, combo_options: Optional[ComboOptions] = None) -> Iterable[Sequence[T]]:
    """Generates the product of a combo, subject to 'combo_options'.

    If 'combo_options' is not specified, 'join_combo' returns
    an Iterable of the product of combo. If 'combo_options' is
    specified, 'join_combo' returns an Iterable of samples of
    the product of combo.

    Sampling should be used to speed up the consumption of the
    returned Iterable as well as to control size of the product,
    especially in cases where oversampling/undersampling is
    desired.

    Args:
        combo: Sequences to join.

        combo_options: Options for randomly sampling.

    Yields:
        A joined combo.

    Examples:
        >>> random.seed(0)
        >>> combo = (('hey', 'ok'), ('speaker', 'sound system'), ('play',))
        >>> tuple(join_combo(combo))
        (('hey', 'speaker', 'play'), ('hey', 'sound system', 'play'),
        ('ok', 'speaker', 'play'), ('ok', 'sound system', 'play'))
        >>> combo_options = ComboOptions(max_sample_size=1, with_replacement=False)
        >>> tuple(join_combo(combo, combo_options=combo_options))
        (('ok', 'sound system', 'play'),)
    """
    if not all(combo):
        raise ValueError('Invalid combo: components must not be empty.')
    if combo_options:
        return _join_with_sampling(combo, combo_options)
    return _join_without_sampling(combo)

def _join_without_sampling(combo: Sequence[Sequence[T]]) -> Iterable[Sequence[T]]:
    return itertools.product(*combo)

def _join_with_sampling(combo: Sequence[Sequence[T]], combo_options: ComboOptions) -> Iterable[Sequence[T]]:
    # Given ((hey speaker, hi speaker), (play, start)), there are 4 possible combinations (2x2=4)
    # choose a random number [0, 3] to represent a random combination.
    # Map that chosen number back to the indices that make the combination.
    # For instance, 0 could map to (0, 0), which would yield "hey speaker play"
    # 1 could map to (1, 0), which would yield "hi speaker play", etc.
    component_lengths = tuple(len(item) for item in combo)
    num_unique_samples = _mul(component_lengths)

    if combo_options.with_replacement:
        sample_size = combo_options.max_sample_size
        flat_item_indices = tuple(random.randint(0, num_unique_samples - 1) for _ in range(sample_size))
    else:
        if num_unique_samples <= sys.maxsize:
            sample_size = min(combo_options.max_sample_size, num_unique_samples)
            if sample_size == num_unique_samples:
                yield from _join_without_sampling(combo)
                return
        else:
            num_unique_samples = sys.maxsize
            sample_size = min(combo_options.max_sample_size, num_unique_samples)

            logger = get_logger(__name__)
            warning_msg = ('Number of possible combinations exceeds sys.maxsize.'
                           ' Sampling from the subset of combinations, sys.maxsize.')
            logger.warning(warning_msg)

            if sample_size == sys.maxsize: # pragma: no cover
                yield from _join_without_sampling(combo)
                return
        flat_item_indices = tuple(random.sample(range(num_unique_samples), sample_size))

    for flat_item_index in flat_item_indices:
        component_indices = _one_d_to_mult_d(flat_item_index, component_lengths)
        combo_components = tuple(combo[component_index][item_index]
                                 for component_index, item_index in enumerate(component_indices))
        yield combo_components

def _one_d_to_mult_d(one_d: int, component_lengths: Sequence[int]) -> Sequence[int]:
    # https://stackoverflow.com/questions/12429492/how-to-convert-a-monodimensional-index-to-corresponding-indices-in-a-multidimens
    indices = []
    for i, component_length in enumerate(component_lengths):
        if component_lengths[i+1:]:
            index = (one_d // _mul(component_lengths[i+1:])) % component_length
        else:
            index = one_d % component_length
        indices.append(index)
    return indices

def _mul(component_lengths: Sequence[int]) -> int:
    return reduce(lambda x, y: x * y, component_lengths)
