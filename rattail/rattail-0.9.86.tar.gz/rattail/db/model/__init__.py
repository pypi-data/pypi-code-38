# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
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
Rattail data models
"""

from __future__ import unicode_literals, absolute_import

from .core import Base, ModelBase, uuid_column, getset_factory, GPCType, Setting, Change, Note
from .contact import PhoneNumber, EmailAddress, MailingAddress

from .people import Person, PersonPhoneNumber, PersonEmailAddress, PersonMailingAddress, PersonNote
from .users import Role, Permission, User, UserRole, UserEvent
from .stores import Store, StorePhoneNumber, StoreEmailAddress
from .customers import (Customer, CustomerPhoneNumber, CustomerEmailAddress, CustomerMailingAddress,
                        CustomerGroup, CustomerGroupAssignment, CustomerPerson, CustomerNote)
from .members import Member, MemberPhoneNumber, MemberEmailAddress, MemberMailingAddress

from .org import Department, Subdepartment, Category, Family, ReportCode, DepositLink
from .employees import (Employee, EmployeePhoneNumber, EmployeeEmailAddress,
                        EmployeeStore, EmployeeDepartment, EmployeeHistory)
from .shifts import ScheduledShift, WorkedShift

from .vendors import Vendor, VendorPhoneNumber, VendorEmailAddress, VendorContact
from .products import (Brand, Tax, Product, ProductImage, ProductCode,
                       ProductCost, ProductFutureCost, ProductPrice,
                       ProductInventory, ProductStoreInfo, ProductVolatile,
                       InventoryAdjustmentReason)
from .purchase import (PurchaseBase, PurchaseItemBase, PurchaseCreditBase,
                       Purchase, PurchaseItem, PurchaseCredit)

from .custorders import CustomerOrder, CustomerOrderItem, CustomerOrderItemEvent

from .messages import Message, MessageRecipient

from .datasync import DataSyncChange
from .labels import LabelProfile
from .bouncer import EmailAttempt, EmailBounce
from .tempmon import TempmonClient, TempmonProbe, TempmonReading
from .upgrades import Upgrade, UpgradeRequirement

from .exports import ExportMixin
from .reports import ReportOutput
from .batch import BatchMixin, BaseFileBatchMixin, FileBatchMixin, BatchRowMixin, ProductBatchRowMixin
from .batch.dynamic import DynamicBatchMixin, ImporterBatch
from .batch.handheld import HandheldBatch, HandheldBatchRow
from .batch.inventory import InventoryBatch, InventoryBatchRow
from .batch.labels import LabelBatch, LabelBatchRow
from .batch.newproduct import NewProductBatch, NewProductBatchRow
from .batch.pricing import PricingBatch, PricingBatchRow
from .batch.product import ProductBatch, ProductBatchRow
from .batch.purchase import PurchaseBatch, PurchaseBatchRow, PurchaseBatchRowClaim, PurchaseBatchCredit
from .batch.vendorcatalog import VendorCatalog, VendorCatalogRow
from .batch.vendorinvoice import VendorInvoice, VendorInvoiceRow
