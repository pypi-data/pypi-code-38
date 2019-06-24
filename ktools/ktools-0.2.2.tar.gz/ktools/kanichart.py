#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 zenbook <zenbook@zenbook-XPS>
#
# Distributed under terms of the MIT license.

"""

"""
import kanichart as kani
import pandas as pd
from .pandas import read_sql
from IPython.display import display, Markdown


def make_sql(company, magic, from_time='2018-10-08'):
    sql = "SELECT open_order_number, profit, close_time, open_magic_number FROM %s_trade_history where open_magic_number > %s and open_magic_number < %s" % \
        (company, magic, magic + 1000)
    sql += " and close_time > '%s' and position_status=5 and open_order_number is not null and close_order_number is not null" % (from_time)
    return sql


def analyze_trade_pair(con, trade_pairs):
    line = kani.LineCharts(width=600)
    all_df = None
    for trade_pair in trade_pairs:
        company, magic = trade_pair
        sql = make_sql(company, magic)
        df = read_sql(sql, con)
        if len(df) > 0:
            df.close_time.fillna(method='ffill', inplace=True)
            df.index = df.close_time
            df = df.reindex()
            df.sort_index(inplace=True)
            profit_cumsum = df["profit"].groupby(df.index).sum().cumsum()
            profit_plot = profit_cumsum.resample('T').last()
            profit_plot.fillna(method='ffill', inplace=True)
            if len(profit_plot) > 0:
                line.add_chart("%s:%d" % (company, magic), profit_plot)
            if all_df is not None:
                all_df = pd.concat([all_df, df], axis=0)
            else:
                all_df = df

    if len(all_df) > 0 and len(trade_pairs) >= 2:
        all_df.close_time.fillna(method='ffill', inplace=True)
        df = all_df.reindex()
        df.sort_index(inplace=True)
        profit_cumsum = df["profit"].groupby(df.index).sum().cumsum()
        profit_plot = profit_cumsum.resample('T').last()
        profit_plot.fillna(method='ffill', inplace=True)
        if len(profit_plot) > 0:
            line.add_chart("ALL", profit_plot)
    return line.plot()


def analyze_company(con, company_names, from_time='2018-10-18'):
    line = kani.LineCharts(width=600)
    for company_name in company_names:
        sql = "SELECT profit, close_time FROM bitcoin.%s_trade_history" % (company_name)
        sql += " where close_time > '%s' and position_status=5 and open_order_number is not null and close_order_number is not null" % (from_time)
        df = read_sql(sql, con)
        df.index = df.close_time
        df.sort_index(inplace=True)
        if len(df) > 0:
            df.close_time.fillna(method='ffill', inplace=True)
            df = df.reindex()
            df.sort_index(inplace=True)
            profit_cumsum = df["profit"].groupby(df.index).sum().cumsum()
            profit_plot = profit_cumsum.resample('T').last()
            profit_plot.fillna(method='ffill', inplace=True)
            if len(profit_plot) > 0:
                line.add_chart(company_name, profit_plot)
    return line.plot()


def analyze_all(con, companies, from_time='2018-10-18'):
    df = None
    for company_name in companies:
        sql = "SELECT profit, close_time FROM bitcoin.%s_trade_history" % (company_name)
        sql += " where close_time > '%s' and position_status=5 and open_order_number is not null and close_order_number is not null" % (from_time)
        tempdf = read_sql(sql, con)
        tempdf.index = tempdf.close_time

        if df is None:
            df = tempdf
        else:
            df = pd.concat([df, tempdf], axis=0)
    line = kani.LineCharts(width=600)
    if len(df) > 0:
        df.close_time.fillna(method='ffill', inplace=True)
        df = df.reindex()
        df.sort_index(inplace=True)
        profit_cumsum = df["profit"].groupby(df.index).sum().cumsum()
        profit_plot = profit_cumsum.resample('T').last()
        profit_plot.fillna(method='ffill', inplace=True)
        if len(profit_plot) > 0:
            line.add_chart("ALL", profit_plot)
    return line.plot()


def plot_take(df, show_title=True):
    if show_title:
        display(Markdown('### All Take Logic'))
    take_df = df[~df['is_making']].copy()
    take_df['cumprofit'] = take_df['profit'].cumsum()
    take_df.index = take_df['close_time']
    take = take_df['cumprofit'].resample('T').last()
    take.fillna(method='ffill', inplace=True)
    line = kani.LineCharts(width=600)
    line.add_chart('take', take)
    return line.plot()


def plot_make(df, show_title=True):
    if show_title:
        display(Markdown('### All Make Logic'))
    make_df = df[df['is_making']].copy()
    make_df['cumprofit'] = make_df['profit'].cumsum()
    make_df.index = make_df['close_time']
    make = make_df['cumprofit'].resample('T').last()
    make.fillna(method='ffill', inplace=True)
    line = kani.LineCharts(width=600)
    line.add_chart('make', make)
    return line.plot()


def plot_make_and_take_with_magic_number(df, magic_number):
    start = magic_number
    end = magic_number + 100
    display(Markdown('### Make magic_number:%s' % (magic_number)))
    display(plot_make(df[(df.open_magic_number > start) & (df.open_magic_number < end)], False))
    display(Markdown('### Take magic_number:%s' % (magic_number)))
    display(plot_take(df[(df.open_magic_number > start) & (df.open_magic_number < end)], False))
