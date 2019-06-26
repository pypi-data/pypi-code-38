# -*- coding: utf-8 -*-


async def calc_blocks_by_days(days):
    return days * 153 if days != 0 else 1
