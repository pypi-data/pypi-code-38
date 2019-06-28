import code
import pstats
from pstats import SortKey

p = pstats.Stats('profile')


def highest_func_maker(key, count=10):
    def highest_func():
        p.sort_stats(key).print_stats(count)
    return highest_func


H_CUM = highest_func_maker(SortKey.CUMULATIVE)
H_TIME = highest_func_maker(SortKey.TIME)


code.interact(local=locals())
