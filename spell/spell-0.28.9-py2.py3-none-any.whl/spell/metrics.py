"""Spell user metrics.

This module is used to log metrics during a Spell run. See :py:func:`send_metric`
function for further documentation. When imported outside of a run on Spell's
infrastructure, this module has no effect.
"""

import os

enabled = False

if os.environ.get("SPELL_RUN"):
    enabled = True
    import requests
    import warnings
    import six

metrics_domain = os.environ.get("SPELL_METRICS") or "metricsfw"


class SpellMetricWarning(Warning):
    """A warning issued if there is an unexpected condition processing a metric"""
    pass


def send_metric(name, value, index=None):
    """Log a metric during a Spell run.

    The code must be executed from within a run on Spell's infrastructure to log the metric.
    If not executed on Spell's infrastructure, this function has no effect.

    Args:
        name (str): the name of the metric to log
        value (str, int, or float): the value of the metric to log
        index (int, optional): the index to associate with this value. If omitted, index will
            be set to 1 + the previous value of index for the metric.
    """
    if not enabled:
        return
    data = {}
    if isinstance(value, (int, float)):
        data["type"] = "number"
        data["number"] = value
    elif isinstance(value, six.string_types):
        data["type"] = "text"
        data["text"] = value
    else:
        warnings.warn("metric discarded: 'value' must be a float, int, or string type (type={})".format(type(value)),
                      SpellMetricWarning)
        return

    if not isinstance(name, six.string_types):
        warnings.warn("metric discarded: 'name' must be a string type (type={})".format(type(name)), SpellMetricWarning)
        return
    data["name"] = name

    if (index is not None) and (not isinstance(index, int)):
        warnings.warn("'index' ignored: must be of type int (type={})".format(type(index)), SpellMetricWarning)
    elif index is not None:
        data["index"] = index

    try:
        url = 'http://{}/user-metrics'.format(metrics_domain)
        r = requests.post(url, json=data)
        if r.status_code == requests.codes.bad_request:
            warnings.warn("metric discarded: {}".format(r.text), SpellMetricWarning)
    except requests.exceptions.RequestException:
        warnings.warn("metric discarded: could not reach {}".format(url), SpellMetricWarning)
