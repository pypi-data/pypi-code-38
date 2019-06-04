# -*- coding: utf-8 -*-
from tg import expose


@expose('activitystream.templates.partials.bootstrap_widget')
def bootstrap_widget(actions, panel_title, panel_body_style, timestamp_since=False, cache_key=None, cache_expire=3600):
    # Note the if cache_key is not None, cache will be enabled and timestamp_since won't works with cache!
    result = dict(
        actions=actions,
        panel_title=panel_title,
        panel_body_style=panel_body_style,
        timestamp_since=timestamp_since
    )
    if cache_key:
        result.update(
            dict(tg_cache=dict(key=cache_key, expire=cache_expire))
        )
    return result

