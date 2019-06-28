# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Example of trees

"""

from ..tree import Tree

simple_numeric = Tree.from_str("1+2*3")

big_sum = Tree.from_str("1+2+3+4+5+6+7+8+9")
big_minus = Tree.from_str("1-2-3-4-5-6-7-8-9")
big_mult = Tree.from_str("1*2*3*4*5*6*7*8*9")
big_sum_of_times = Tree.from_str("1*2+3*4+5*6+7*8+9*10")

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
