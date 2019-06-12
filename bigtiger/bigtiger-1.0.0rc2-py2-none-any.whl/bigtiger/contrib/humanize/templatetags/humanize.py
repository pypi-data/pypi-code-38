# -*- coding: utf-8 -*-

from datetime import datetime

from django import template

register = template.Library()


@register.inclusion_tag('humanize/tags/daterange.htm')
def daterange_tag(begin_date=None, end_date=None,
                  date_fmt='yyyy-MM-dd HH:mm:ss', moment_fmt='YYYY-MM-DD HH:mm:ss', date_humanize=None):
    """时间范围快捷选择 tag
    @param begin_date: 开始时间, 默认值：系统当前时间
    @param end_date: 结束结束时间, 默认值：开始时间
    @param date_fmt: 日期选择控件的format，默认值：yyyy-MM-dd HH:mm:ss
    @param moment_fmt: moment的format， 默认值：YYYY-MM-DD HH:mm:ss'
    @param date_humanize: 快捷时间的人性化显示， 默认值：None，显示为开始时间至结束时间

    @return: 返回模版需要的context
    """

    if not begin_date:
        begin_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if not end_date:
        end_date = begin_date

    return {
        'begin_date': begin_date,
        'end_date': end_date,
        'date_fmt': date_fmt or 'yyyy-MM-dd HH:mm:ss',
        'moment_fmt': moment_fmt or 'YYYY-MM-DD HH:mm:ss',
        'date_humanize': date_humanize or '{} 至 {}'.format(begin_date, end_date)
    }
