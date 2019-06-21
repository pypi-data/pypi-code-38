#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Sets-up parallel processing using all available processors"""

import multiprocessing
parallel = multiprocessing.cpu_count()
"""The number of processes to spawn for a given run

The default is the value returned by :py:func:`multiprocessing.cpu_count` on
**your** machine (disregard the value above). If you want to tune it, using the
``--parallel`` command-line option or the attribute ``parallel`` on a
configuration file read **after** this one.
"""

nice = 10
"""Operating system priority (the higher the smaller)

This value controls the execution priority for jobs launched by a run of
the verification scripts. By default, jobs would be launched with priority of
zero if this setting is not in place. By increasing the value (i.e., reducing
the priority of spawn processes), existing programs already running on your
desktop (such as your web browser) will have more priority and won't become
irresponsive.

Setting this value is optional, but you cannot set it to value smaller than
zero (the default). The maximum is 19. You may read the manual for `renice` for
more information about this setting.
"""
