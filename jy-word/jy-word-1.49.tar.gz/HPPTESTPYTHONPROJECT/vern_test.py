# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2019/5/23 0023
__author__ = 'huohuo'
from matplotlib import pyplot as plt
from matplotlib_venn import venn2
from jy_word.File import File
my_file = File()


def set_info(file_name):
    set11 = my_file.read(file_name).strip('\n').split('\n')
    return set(set11), file_name


if __name__ == "__main__":
    set1, l1 = set_info('nodbsnp.list')
    set2, l2 = set_info('hg19_id.list')
    venn2(subsets=[set1, set2], set_labels=(l1, l2), set_colors=['r', 'g'])
    plt.savefig('test.png')
    pass
    

