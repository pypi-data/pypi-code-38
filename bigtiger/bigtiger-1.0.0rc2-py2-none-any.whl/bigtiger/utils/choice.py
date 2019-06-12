# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import functools


def choice_wrap(all_code=None, all_text=None, null_code=None, null_text=None):
    """为choice 添加全部选择项和空选项的装饰器"""

    all_code = all_code or '*'
    all_text = all_text or '全部'

    null_code = null_code or ''
    null_text = null_text or '[请选择]'

    def _choice_wrap(fn):
        @functools.wraps(fn)
        def __choice_wrap(*args, **kwargs):
            result = fn(*args, **kwargs)

            if kwargs.get('auto_sort', True):
                result = sorted(result, key=lambda item: item[0])
            if kwargs.get('is_all', False):
                result.insert(0, (all_code, all_text))
            if kwargs.get('is_null', False):
                result.insert(0, (null_code, null_text))

            return result
        return __choice_wrap
    return _choice_wrap
