# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Common setting definitions
"""

from __future__ import unicode_literals, absolute_import


class Setting(object):
    """
    Base class for all setting definitions.
    """
    group = "(General)"
    namespace = None
    name = None
    data_type = str
    choices = None
    required = False


##############################
# (General)
##############################

class rattail_app_title(Setting):
    """
    Official display title for the app.
    """
    namespace = 'rattail'
    name = 'app_title'


class rattail_node_title(Setting):
    """
    Official display title for the app node.
    """
    namespace = 'rattail'
    name = 'node_title'


class rattail_production(Setting):
    """
    If set, the app is considered to be running in "production" mode, whereas
    if disabled, the app is considered to be running in development / testing /
    staging mode.
    """
    namespace = 'rattail'
    name = 'production'
    data_type = bool


class tailbone_background_color(Setting):
    """
    Background color for this app node.  If unset, default color is white.
    """
    namespace = 'tailbone'
    name = 'background_color'


class rattail_single_store(Setting):
    """
    If set, the app should assume there is only one Store record, and that all
    purchases etc. will pertain to it.
    """
    namespace = 'rattail'
    name = 'single_store'
    data_type = bool


class rattail_demo(Setting):
    """
    If set, the app is considered to be running in "demo" mode.
    """
    namespace = 'rattail'
    name = 'demo'
    data_type = bool


class rattail_appdir(Setting):
    """
    Path to the "app" dir for the running instance.
    """
    namespace = 'rattail'
    name = 'appdir'


class rattail_workdir(Setting):
    """
    Path to the "work" dir for the running instance.
    """
    namespace = 'rattail'
    name = 'workdir'


##############################
# DataSync
##############################

class rattail_datasync_url(Setting):
    """
    URL for datasync change queue.
    """
    group = "DataSync"
    namespace = 'rattail.datasync'
    name = 'url'


class tailbone_datasync_restart(Setting):
    """
    Command used when restarting the datasync daemon.
    """
    group = "DataSync"
    namespace = 'tailbone'
    name = 'datasync.restart'


##############################
# Email
##############################

class rattail_mail_record_attempts(Setting):
    """
    If enabled, this flag will cause Email Attempts to be recorded in the
    database, for "most" attempts to send email.
    """
    group = "Email"
    namespace = 'rattail.mail'
    name = 'record_attempts'
    data_type = bool


##############################
# FileMon
##############################

class tailbone_filemon_restart(Setting):
    """
    Command used when restarting the filemon daemon.
    """
    group = "FileMon"
    namespace = 'tailbone'
    name = 'filemon.restart'


##############################
# Products
##############################

class rattail_product_key(Setting):
    """
    Defines which of the possible "product key" fields should be effectively
    treated as the product key.
    """
    group = "Products"
    namespace = 'rattail'
    name = 'product.key'
    choices = [
        'upc',
        'item_id',
        'scancode',
    ]


class rattail_product_key_title(Setting):
    """
    Defines the official "title" (display name) for the product key field.
    """
    group = "Products"
    namespace = 'rattail'
    name = 'product.key_title'


class rattail_products_mobile_quick_lookup(Setting):
    """
    If set, the mobile Products page will only allow "quick lookup" access to
    product records.  If NOT set, then the typical record listing is shown.
    """
    group = "Products"
    namespace = 'rattail'
    name = 'products.mobile.quick_lookup'
    data_type = bool


##############################
# Purchasing / Receiving
##############################

class rattail_batch_purchase_allow_cases(Setting):
    """
    Determines whether or not "cases" is a valid UOM for ordering, receiving etc.
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.allow_cases'
    data_type = bool


class rattail_batch_purchase_allow_expired_credits(Setting):
    """
    Determines whether or not "expired" is a valid type for purchase credits.
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.allow_expired_credits'
    data_type = bool


class rattail_batch_purchase_mobile_images(Setting):
    """
    If set, product images will be displayed when viewing a purchasing batch row.
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.mobile_images'
    data_type = bool


class rattail_batch_purchase_mobile_quick_receive(Setting):
    """
    If set, a "quick receive" button will be available for mobile receiving.
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.mobile_quick_receive'
    data_type = bool


class rattail_batch_purchase_mobile_quick_receive_all(Setting):
    """
    If set, the mobile "quick receive" button will receive "all" (remaining
    quantity) for the item, instead of "one".
    """
    group = "Purchasing / Receiving"
    namespace = 'rattail.batch'
    name = 'purchase.mobile_quick_receive_all'
    data_type = bool


##############################
# Vendors
##############################

class rattail_vendor_use_autocomplete(Setting):
    """
    If set, `vendor` fields will use the autocomplete widget; otherwise such
    fields will use a drop-down (select) widget.
    """
    group = "Vendors"
    namespace = 'rattail'
    name = 'vendor.use_autocomplete'
    data_type = bool
