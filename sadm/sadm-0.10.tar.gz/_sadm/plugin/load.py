# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

# register plugins (order really matters)

import _sadm.plugin.sadm
import _sadm.plugin.sadmenv

# os stuff should be done before sync assets are deployed

import _sadm.plugin.os
import _sadm.plugin.os.pkg
import _sadm.plugin.os.user

# deploy assets after all os stuff was done but before services/apps setup
# so services/apps deploy can use built (already deployed) assets

import _sadm.plugin.sync

# network plugins

import _sadm.plugin.network.iptables

# service plugins

import _sadm.plugin.service.munin
import _sadm.plugin.service.munin_node

# services that depend on apache should go before it
# so apache is restarted after all deps were setup

import _sadm.plugin.service.apache
