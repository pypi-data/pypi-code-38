#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: 
# @file: project2lines.py
# @time: 2018/8/1 15:49
# @Software: PyCharm

import os
import re
import warnings

from astartool.project._project import project_to_lines, file_to_lines, walk

project_to_lines = project_to_lines
file_to_lines = file_to_lines
walk = walk
if __name__ == '__main__':
    project_to_lines(src_project='E:/cxl/codes/python/snowland-algorithm-python',
                     # start_file='\n' + '-' * 15 + '\n',
                     # end_file='\n' + '-' * 15 + '\n\n'
                     allow_extension=['.py',
                                      '.jl',
                                      '.m',
                                      '.js',
                                      '.java',
                                      '.xml',
                                      '.html',
                                      '.htm',
                                      '.css',
                                      '.cs',
                                      '.cpp',
                                      '.c',
                                      '.h',
                                      '.php'],
                     ignore=[]
                     )
