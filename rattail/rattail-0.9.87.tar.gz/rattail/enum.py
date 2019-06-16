# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
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
**Enumerations**

The following enumerations are provided:

.. attribute:: BATCH_ACTION

   Action types for use with batches.  These are taken from the SIL
   specification.

.. attribute:: EMAIL_PREFERENCE

   Various options indicating a person's preferences on whether to receive
   email, and if so, in what format.

.. attribute:: EMPLOYEE_STATUS

   Status types for employees (e.g. current, former).

.. attribute:: PHONE_TYPE

   Various "types" of phone contact information (e.g. home, work).

.. attribute:: PRICE_TYPE

   Various types of prices which may exist for a product.  These are taken from
   the SIL specification.

.. attribute:: UNIT_OF_MEASURE

   Units of measure for use with products (e.g. each, pound).  These are taken
   from the SIL specification.
"""

from __future__ import unicode_literals


BATCH_ACTION_ADD                = 'ADD'
BATCH_ACTION_ADD_REPLACE        = 'ADDRPL'
BATCH_ACTION_CHANGE             = 'CHANGE'
BATCH_ACTION_LOAD               = 'LOAD'
BATCH_ACTION_REMOVE             = 'REMOVE'

BATCH_ACTION = {
    BATCH_ACTION_ADD            : "Add",
    BATCH_ACTION_ADD_REPLACE    : "Add/Replace",
    BATCH_ACTION_CHANGE         : "Change",
    BATCH_ACTION_LOAD           : "Load",
    BATCH_ACTION_REMOVE         : "Remove",
    }


EMAIL_ATTEMPT_CREATED           = 0
EMAIL_ATTEMPT_SUCCESS           = 1
EMAIL_ATTEMPT_FAILURE           = 2
# EMAIL_ATTEMPT_BOUNCED           = 3

EMAIL_ATTEMPT = {
    EMAIL_ATTEMPT_CREATED       : "created",
    EMAIL_ATTEMPT_SUCCESS       : "success",
    EMAIL_ATTEMPT_FAILURE       : "failure",
    # EMAIL_ATTEMPT_BOUNCED       : "bounced",
}


EMAIL_PREFERENCE_NONE           = 0
EMAIL_PREFERENCE_TEXT           = 1
EMAIL_PREFERENCE_HTML           = 2
EMAIL_PREFERENCE_MOBILE         = 3

EMAIL_PREFERENCE = {
    EMAIL_PREFERENCE_NONE       : "No Emails",
    EMAIL_PREFERENCE_TEXT       : "Text",
    EMAIL_PREFERENCE_HTML       : "HTML",
    EMAIL_PREFERENCE_MOBILE     : "Mobile",
    }


HANDHELD_DEVICE_TYPE_MOTOROLA           = 'motorola'
HANDHELD_DEVICE_TYPE_PALMOS             = 'palmos'

HANDHELD_DEVICE_TYPE = {
    HANDHELD_DEVICE_TYPE_MOTOROLA       : "Motorola",
    HANDHELD_DEVICE_TYPE_PALMOS         : "PalmOS",
}


IMPORTER_BATCH_ROW_STATUS_NOCHANGE      = 0
IMPORTER_BATCH_ROW_STATUS_CREATE        = 1
IMPORTER_BATCH_ROW_STATUS_UPDATE        = 2
IMPORTER_BATCH_ROW_STATUS_DELETE        = 3

IMPORTER_BATCH_ROW_STATUS = {
    IMPORTER_BATCH_ROW_STATUS_NOCHANGE  : "no change",
    IMPORTER_BATCH_ROW_STATUS_CREATE    : "create",
    IMPORTER_BATCH_ROW_STATUS_UPDATE    : "update",
    IMPORTER_BATCH_ROW_STATUS_DELETE    : "delete",
}


INVENTORY_MODE_REPLACE          = 1
INVENTORY_MODE_REPLACE_ADJUST   = 2
INVENTORY_MODE_ADJUST           = 3
INVENTORY_MODE_ZERO_ALL         = 4
INVENTORY_MODE_VARIANCE         = 5

INVENTORY_MODE = {
    INVENTORY_MODE_REPLACE              : "Replace only",
    INVENTORY_MODE_REPLACE_ADJUST       : "Replace then adjust",
    INVENTORY_MODE_ADJUST               : "Adjust only",
    INVENTORY_MODE_ZERO_ALL             : "Zero all",
    INVENTORY_MODE_VARIANCE             : "Variance Correction",
}


MESSAGE_STATUS_INBOX            = 1
MESSAGE_STATUS_ARCHIVE          = 2

MESSAGE_STATUS = {
    MESSAGE_STATUS_INBOX        : "Inbox",
    MESSAGE_STATUS_ARCHIVE      : "Archive",
}


PHONE_TYPE_HOME                 = 'home'
PHONE_TYPE_MOBILE               = 'mobile'
PHONE_TYPE_OTHER                = 'other'

PHONE_TYPE = {
    PHONE_TYPE_HOME             : "Home",
    PHONE_TYPE_MOBILE           : "Mobile",
    PHONE_TYPE_OTHER            : "Other",
    }


PRICE_TYPE_REGULAR              = 0
PRICE_TYPE_TPR                  = 1
PRICE_TYPE_SALE                 = 2
PRICE_TYPE_MANAGER_SPECIAL      = 3
PRICE_TYPE_ALTERNATE            = 4
PRICE_TYPE_FREQUENT_SHOPPER     = 5
PRICE_TYPE_MFR_SUGGESTED        = 901

PRICE_TYPE = {
    PRICE_TYPE_REGULAR          : "Regular Price",
    PRICE_TYPE_TPR              : "TPR",
    PRICE_TYPE_SALE             : "Sale",
    PRICE_TYPE_MANAGER_SPECIAL  : "Manager Special",
    PRICE_TYPE_ALTERNATE        : "Alternate Price",
    PRICE_TYPE_FREQUENT_SHOPPER : "Frequent Shopper",
    PRICE_TYPE_MFR_SUGGESTED    : "Manufacturer's Suggested",
    }


PURCHASE_BATCH_MODE_ORDERING            = 10
PURCHASE_BATCH_MODE_RECEIVING           = 20
PURCHASE_BATCH_MODE_COSTING             = 30

PURCHASE_BATCH_MODE = {
    PURCHASE_BATCH_MODE_ORDERING        : "ordering",
    PURCHASE_BATCH_MODE_RECEIVING       : "receiving",
    PURCHASE_BATCH_MODE_COSTING         : "invoicing",
}


PURCHASE_CREDIT_STATUS_NEW              = 10
PURCHASE_CREDIT_STATUS_SUBMITTED        = 20
PURCHASE_CREDIT_STATUS_SATISFIED        = 30
PURCHASE_CREDIT_STATUS_NONCREDITABLE    = 40

PURCHASE_CREDIT_STATUS = {
    PURCHASE_CREDIT_STATUS_NEW          : "new",
    PURCHASE_CREDIT_STATUS_SUBMITTED    : "submitted",
    PURCHASE_CREDIT_STATUS_SATISFIED    : "satisfied",
    PURCHASE_CREDIT_STATUS_NONCREDITABLE: "non-creditable",
}


PURCHASE_STATUS_NEW             = 1 # TODO: is this needed?
PURCHASE_STATUS_ORDERED         = 10
PURCHASE_STATUS_RECEIVED        = 20
PURCHASE_STATUS_COSTED          = 30
PURCHASE_STATUS_PAID            = 40

PURCHASE_STATUS = {
    PURCHASE_STATUS_NEW         : "new/pending",
    PURCHASE_STATUS_ORDERED     : "ordered",
    PURCHASE_STATUS_RECEIVED    : "received",
    PURCHASE_STATUS_COSTED      : "invoiced",
    PURCHASE_STATUS_PAID        : "paid",
}


TEMPMON_APPLIANCE_TYPE_COOLER           = 1
TEMPMON_APPLIANCE_TYPE_FREEZER          = 2

TEMPMON_APPLIANCE_TYPE = {
    TEMPMON_APPLIANCE_TYPE_COOLER       : "cooler",
    TEMPMON_APPLIANCE_TYPE_FREEZER      : "freezer",
}


TEMPMON_DISK_TYPE_SDCARD                = 1
TEMPMON_DISK_TYPE_USB                   = 2

TEMPMON_DISK_TYPE = {
    TEMPMON_DISK_TYPE_SDCARD            : "SD card",
    TEMPMON_DISK_TYPE_USB               : "USB",
}


TEMPMON_PROBE_STATUS_GOOD_TEMP          = 1
TEMPMON_PROBE_STATUS_LOW_TEMP           = 2
TEMPMON_PROBE_STATUS_HIGH_TEMP          = 3
TEMPMON_PROBE_STATUS_CRITICAL_HIGH_TEMP = 4
# TODO: deprecate / remove this one
TEMPMON_PROBE_STATUS_CRITICAL_TEMP      = TEMPMON_PROBE_STATUS_CRITICAL_HIGH_TEMP
TEMPMON_PROBE_STATUS_ERROR              = 5
TEMPMON_PROBE_STATUS_CRITICAL_LOW_TEMP  = 6

TEMPMON_PROBE_STATUS = {
    TEMPMON_PROBE_STATUS_CRITICAL_HIGH_TEMP     : "critical high temp",
    # TODO: deprecate / remove this one
    TEMPMON_PROBE_STATUS_CRITICAL_TEMP          : "critical high temp",
    TEMPMON_PROBE_STATUS_HIGH_TEMP              : "high temp",
    TEMPMON_PROBE_STATUS_GOOD_TEMP              : "good temp",
    TEMPMON_PROBE_STATUS_LOW_TEMP               : "low temp",
    TEMPMON_PROBE_STATUS_CRITICAL_LOW_TEMP      : "critical low temp",
    TEMPMON_PROBE_STATUS_ERROR                  : "error",
}


# These values are taken from the SIL standard.
UNIT_OF_MEASURE_NONE                    = '00'
UNIT_OF_MEASURE_EACH                    = '01'
UNIT_OF_MEASURE_10_COUNT                = '02'
UNIT_OF_MEASURE_DOZEN                   = '03'
UNIT_OF_MEASURE_50_COUNT                = '04'
UNIT_OF_MEASURE_100_COUNT               = '05'
UNIT_OF_MEASURE_100_COUNT_1_PLY         = '06'
UNIT_OF_MEASURE_100_COUNT_2_PLY         = '07'
UNIT_OF_MEASURE_100_COUNT_3_PLY         = '08'
UNIT_OF_MEASURE_100_COUNT_4_PLY         = '09'
UNIT_OF_MEASURE_INCH                    = '21'
UNIT_OF_MEASURE_FOOT                    = '22'
UNIT_OF_MEASURE_50_FEET                 = '23'
UNIT_OF_MEASURE_100_FEET                = '24'
UNIT_OF_MEASURE_100_YARDS               = '25'
UNIT_OF_MEASURE_SQUARE_INCH             = '31'
UNIT_OF_MEASURE_SQUARE_FEET             = '32'
UNIT_OF_MEASURE_50_SQUARE_YARD          = '34'
UNIT_OF_MEASURE_LIQUID_OUNCE            = '41'
UNIT_OF_MEASURE_PINT                    = '42'
UNIT_OF_MEASURE_QUART                   = '43'
UNIT_OF_MEASURE_HALF_GALLON             = '44'
UNIT_OF_MEASURE_GALLON                  = '45'
UNIT_OF_MEASURE_DRY_OUNCE               = '48'
UNIT_OF_MEASURE_POUND                   = '49'
UNIT_OF_MEASURE_MILLIMETER              = '61'
UNIT_OF_MEASURE_CENTIMETER              = '62'
UNIT_OF_MEASURE_DECIMETER               = '63'
UNIT_OF_MEASURE_METER                   = '64'
UNIT_OF_MEASURE_DEKAMETER               = '65'
UNIT_OF_MEASURE_HECTOMETER              = '66'
UNIT_OF_MEASURE_SQ_CENTIMETER           = '71'
UNIT_OF_MEASURE_SQUARE_METER            = '72'
UNIT_OF_MEASURE_CENTILITER              = '81'
UNIT_OF_MEASURE_GRAMS                   = '86'
UNIT_OF_MEASURE_KILOGRAMS               = '87'
UNIT_OF_MEASURE_BOX                     = '100'
UNIT_OF_MEASURE_CARTON                  = '101'
UNIT_OF_MEASURE_CASE                    = '102'
UNIT_OF_MEASURE_PACKAGE                 = '103'
UNIT_OF_MEASURE_PACK                    = '104'
UNIT_OF_MEASURE_ROLL                    = '105'
UNIT_OF_MEASURE_GROSS                   = '106'
UNIT_OF_MEASURE_LOAD                    = '107'
UNIT_OF_MEASURE_COUNT                   = '108'
UNIT_OF_MEASURE_YARD                    = '109'
UNIT_OF_MEASURE_BUSHEL                  = '110'
UNIT_OF_MEASURE_CENTIGRAM               = '111'
UNIT_OF_MEASURE_DECILITER               = '112'
UNIT_OF_MEASURE_DECIGRAM                = '113'
UNIT_OF_MEASURE_MILLILITER              = '114'
UNIT_OF_MEASURE_PECK                    = '115'
UNIT_OF_MEASURE_PAIR                    = '116'
UNIT_OF_MEASURE_DRY_QUART               = '117'
UNIT_OF_MEASURE_SHEET                   = '118'
UNIT_OF_MEASURE_STICKS                  = '120'
UNIT_OF_MEASURE_THOUSAND                = '121'
UNIT_OF_MEASURE_PALLET_UNIT_LOAD        = '122'
UNIT_OF_MEASURE_PERCENT                 = '123'
UNIT_OF_MEASURE_TRUCKLOAD               = '124'
UNIT_OF_MEASURE_DOLLARS                 = '125'

# These values are *not* from the SIL standard.
UNIT_OF_MEASURE_BUNCH                   = '300'
UNIT_OF_MEASURE_LITER                   = '301'
UNIT_OF_MEASURE_BAG                     = '302'
UNIT_OF_MEASURE_CAPSULES                = '303'
UNIT_OF_MEASURE_CUBIC_CENTIMETERS       = '304'
UNIT_OF_MEASURE_SOFTGELS                = '305'
UNIT_OF_MEASURE_TABLETS                 = '306'
UNIT_OF_MEASURE_VEG_CAPSULES            = '307'
UNIT_OF_MEASURE_WAFERS                  = '308'
UNIT_OF_MEASURE_PIECE                   = '309'
UNIT_OF_MEASURE_KIT                     = '310'
UNIT_OF_MEASURE_CHEWABLE                = '311'
UNIT_OF_MEASURE_LOZENGE                 = '312'
UNIT_OF_MEASURE_CUBIC_INCH              = '313'
UNIT_OF_MEASURE_VEG_SOFTGEL             = '314'
UNIT_OF_MEASURE_CUBIC_FOOT              = '315'
UNIT_OF_MEASURE_PACKET                  = '316'
UNIT_OF_MEASURE_DOSE                    = '317'

UNIT_OF_MEASURE = {

    # standard
    UNIT_OF_MEASURE_NONE                : "None",
    UNIT_OF_MEASURE_EACH                : "Each",
    UNIT_OF_MEASURE_10_COUNT            : "10 Count",
    UNIT_OF_MEASURE_DOZEN               : "Dozen",
    UNIT_OF_MEASURE_50_COUNT            : "50-Count",
    UNIT_OF_MEASURE_100_COUNT           : "100-Count",
    UNIT_OF_MEASURE_100_COUNT_1_PLY     : "100-Count (1 Ply)",
    UNIT_OF_MEASURE_100_COUNT_2_PLY     : "100-Count (2 Ply)",
    UNIT_OF_MEASURE_100_COUNT_3_PLY     : "100-Count (3 Ply)",
    UNIT_OF_MEASURE_100_COUNT_4_PLY     : "100-Count (4 Ply)",
    UNIT_OF_MEASURE_INCH                : "Inch",
    UNIT_OF_MEASURE_FOOT                : "Foot",
    UNIT_OF_MEASURE_50_FEET             : "50 Feet",
    UNIT_OF_MEASURE_100_FEET            : "100 Feet",
    UNIT_OF_MEASURE_100_YARDS           : "100 Yards",
    UNIT_OF_MEASURE_SQUARE_INCH         : "Square Inch",
    UNIT_OF_MEASURE_SQUARE_FEET         : "Square feet",
    UNIT_OF_MEASURE_50_SQUARE_YARD      : "50 Square yard",
    UNIT_OF_MEASURE_LIQUID_OUNCE        : "Liquid ounce",
    UNIT_OF_MEASURE_PINT                : "Pint",
    UNIT_OF_MEASURE_QUART               : "Quart",
    UNIT_OF_MEASURE_HALF_GALLON         : "Half gallon",
    UNIT_OF_MEASURE_GALLON              : "Gallon",
    UNIT_OF_MEASURE_DRY_OUNCE           : "Dry ounce",
    UNIT_OF_MEASURE_POUND               : "Pound",
    UNIT_OF_MEASURE_MILLIMETER          : "Millimeter",
    UNIT_OF_MEASURE_CENTIMETER          : "Centimeter",
    UNIT_OF_MEASURE_DECIMETER           : "Decimeter",
    UNIT_OF_MEASURE_METER               : "Meter",
    UNIT_OF_MEASURE_DEKAMETER           : "Dekameter",
    UNIT_OF_MEASURE_HECTOMETER          : "Hectometer",
    UNIT_OF_MEASURE_SQ_CENTIMETER       : "Sq. Centimeter",
    UNIT_OF_MEASURE_SQUARE_METER        : "Square Meter",
    UNIT_OF_MEASURE_CENTILITER          : "Centiliter",
    UNIT_OF_MEASURE_GRAMS               : "Grams",
    UNIT_OF_MEASURE_KILOGRAMS           : "Kilograms",
    UNIT_OF_MEASURE_BOX                 : "Box",
    UNIT_OF_MEASURE_CARTON              : "Carton",
    UNIT_OF_MEASURE_CASE                : "Case",
    UNIT_OF_MEASURE_PACKAGE             : "Package",
    UNIT_OF_MEASURE_PACK                : "Pack",
    UNIT_OF_MEASURE_ROLL                : "Roll",
    UNIT_OF_MEASURE_GROSS               : "Gross",
    UNIT_OF_MEASURE_LOAD                : "Load",
    UNIT_OF_MEASURE_COUNT               : "Count",
    UNIT_OF_MEASURE_YARD                : "Yard",
    UNIT_OF_MEASURE_BUSHEL              : "Bushel",
    UNIT_OF_MEASURE_CENTIGRAM           : "Centigram",
    UNIT_OF_MEASURE_DECILITER           : "Deciliter",
    UNIT_OF_MEASURE_DECIGRAM            : "Decigram",
    UNIT_OF_MEASURE_MILLILITER          : "Milliliter",
    UNIT_OF_MEASURE_PECK                : "Peck",
    UNIT_OF_MEASURE_PAIR                : "Pair",
    UNIT_OF_MEASURE_DRY_QUART           : "Quart (Dry)",
    UNIT_OF_MEASURE_SHEET               : "Sheet",
    UNIT_OF_MEASURE_STICKS              : "Sticks",
    UNIT_OF_MEASURE_THOUSAND            : "Thousand",
    UNIT_OF_MEASURE_PALLET_UNIT_LOAD    : "Pallet/Unit Load",
    UNIT_OF_MEASURE_PERCENT             : "Percent",
    UNIT_OF_MEASURE_TRUCKLOAD           : "Truckload",
    UNIT_OF_MEASURE_DOLLARS             : "Dollars",

    # non-standard
    UNIT_OF_MEASURE_BUNCH               : "Bunch",
    UNIT_OF_MEASURE_LITER               : "Liter",
    UNIT_OF_MEASURE_BAG                 : "Bag",
    UNIT_OF_MEASURE_CAPSULES            : "Capsules",
    UNIT_OF_MEASURE_CUBIC_CENTIMETERS   : "Cubic Centimeters",
    UNIT_OF_MEASURE_SOFTGELS            : "Soft Gels",
    UNIT_OF_MEASURE_TABLETS             : "Tablets",
    UNIT_OF_MEASURE_VEG_CAPSULES        : "Vegetarian Capsules",
    UNIT_OF_MEASURE_WAFERS              : "Wafers",
    UNIT_OF_MEASURE_PIECE               : "Piece",
    UNIT_OF_MEASURE_KIT                 : "Kit",
    UNIT_OF_MEASURE_CHEWABLE            : "Chewable",
    UNIT_OF_MEASURE_LOZENGE             : "Lozenge",
    UNIT_OF_MEASURE_CUBIC_INCH          : "Cubic Inches",
    UNIT_OF_MEASURE_VEG_SOFTGEL         : "Vegitarian Softgels",
    UNIT_OF_MEASURE_CUBIC_FOOT          : "Cubic Feet",
    UNIT_OF_MEASURE_PACKET              : "Packets",
    UNIT_OF_MEASURE_DOSE                : "Doses",
    }


UPGRADE_STATUS_PENDING          = 1
UPGRADE_STATUS_EXECUTING        = 2
UPGRADE_STATUS_SUCCEEDED        = 3
UPGRADE_STATUS_FAILED           = 4

UPGRADE_STATUS = {
    UPGRADE_STATUS_PENDING      : "pending execution",
    UPGRADE_STATUS_EXECUTING    : "currently executing",
    UPGRADE_STATUS_SUCCEEDED    : "execution succeeded",
    UPGRADE_STATUS_FAILED       : "execution failed",
}


USER_EVENT_LOGIN                = 1
USER_EVENT_LOGOUT               = 2
USER_EVENT_BECOME_ROOT          = 3
USER_EVENT_STOP_ROOT            = 4

USER_EVENT = {
    USER_EVENT_LOGIN            : "login",
    USER_EVENT_LOGOUT           : "logout",
    USER_EVENT_BECOME_ROOT      : "become root",
    USER_EVENT_STOP_ROOT        : "stop being root",
}


EMPLOYEE_STATUS_CURRENT         = 1
EMPLOYEE_STATUS_FORMER          = 2

EMPLOYEE_STATUS = {
    EMPLOYEE_STATUS_CURRENT     : "current",
    EMPLOYEE_STATUS_FORMER      : "former",
    }


# VENDOR_CATALOG_NOT_PARSED       = 1
# VENDOR_CATALOG_PARSED           = 2
# VENDOR_CATALOG_COGNIZED         = 3
# VENDOR_CATALOG_PROCESSED        = 4

# VENDOR_CATALOG_STATUS = {
#     VENDOR_CATALOG_NOT_PARSED   : "not parsed",
#     VENDOR_CATALOG_PARSED       : "parsed",
#     VENDOR_CATALOG_COGNIZED     : "cognized",
#     VENDOR_CATALOG_PROCESSED    : "processed",
#     }


TRAINWRECK_SYSTEM = {}
