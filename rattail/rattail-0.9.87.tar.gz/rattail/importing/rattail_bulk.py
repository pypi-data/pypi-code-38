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
Rattail -> Rattail bulk data import
"""

from __future__ import unicode_literals, absolute_import

from rattail import importing
from rattail.util import OrderedDict
from rattail.importing.rattail import FromRattailToRattailImport, FromRattail


class BulkFromRattailToRattail(FromRattailToRattailImport, importing.BulkImportHandler):
    """
    Handler for Rattail -> Rattail bulk data import.
    """

    def get_importers(self):
        importers = OrderedDict()
        importers['Person'] = PersonImporter
        importers['PersonEmailAddress'] = PersonEmailAddressImporter
        importers['PersonPhoneNumber'] = PersonPhoneNumberImporter
        importers['PersonMailingAddress'] = PersonMailingAddressImporter
        importers['User'] = UserImporter
        importers['Message'] = MessageImporter
        importers['MessageRecipient'] = MessageRecipientImporter
        importers['Store'] = StoreImporter
        importers['StorePhoneNumber'] = StorePhoneNumberImporter
        importers['Employee'] = EmployeeImporter
        importers['EmployeeStore'] = EmployeeStoreImporter
        importers['EmployeeEmailAddress'] = EmployeeEmailAddressImporter
        importers['EmployeePhoneNumber'] = EmployeePhoneNumberImporter
        importers['ScheduledShift'] = ScheduledShiftImporter
        importers['WorkedShift'] = WorkedShiftImporter
        importers['Customer'] = CustomerImporter
        importers['CustomerGroup'] = CustomerGroupImporter
        importers['CustomerGroupAssignment'] = CustomerGroupAssignmentImporter
        importers['CustomerPerson'] = CustomerPersonImporter
        importers['CustomerEmailAddress'] = CustomerEmailAddressImporter
        importers['CustomerPhoneNumber'] = CustomerPhoneNumberImporter
        importers['Vendor'] = VendorImporter
        importers['VendorEmailAddress'] = VendorEmailAddressImporter
        importers['VendorPhoneNumber'] = VendorPhoneNumberImporter
        importers['VendorContact'] = VendorContactImporter
        importers['Department'] = DepartmentImporter
        importers['EmployeeDepartment'] = EmployeeDepartmentImporter
        importers['Subdepartment'] = SubdepartmentImporter
        importers['Category'] = CategoryImporter
        importers['Family'] = FamilyImporter
        importers['ReportCode'] = ReportCodeImporter
        importers['DepositLink'] = DepositLinkImporter
        importers['Tax'] = TaxImporter
        importers['Brand'] = BrandImporter
        importers['Product'] = ProductImporter
        importers['ProductCode'] = ProductCodeImporter
        importers['ProductCost'] = ProductCostImporter
        importers['ProductPrice'] = ProductPriceImporter
        return importers


class BulkFromRattail(FromRattail, importing.BulkToPostgreSQL):
    """
    Base class for bulk Rattail -> Rattail importers.
    """


class PersonImporter(BulkFromRattail, importing.model.PersonImporter):
    pass

class PersonEmailAddressImporter(BulkFromRattail, importing.model.PersonEmailAddressImporter):
    pass

class PersonPhoneNumberImporter(BulkFromRattail, importing.model.PersonPhoneNumberImporter):
    pass

class PersonMailingAddressImporter(BulkFromRattail, importing.model.PersonMailingAddressImporter):
    pass

class UserImporter(BulkFromRattail, importing.model.UserImporter):
    pass

class MessageImporter(BulkFromRattail, importing.model.MessageImporter):
    pass

class MessageRecipientImporter(BulkFromRattail, importing.model.MessageRecipientImporter):
    pass

class StoreImporter(BulkFromRattail, importing.model.StoreImporter):
    pass

class StorePhoneNumberImporter(BulkFromRattail, importing.model.StorePhoneNumberImporter):
    pass

class EmployeeImporter(BulkFromRattail, importing.model.EmployeeImporter):
    pass

class EmployeeStoreImporter(BulkFromRattail, importing.model.EmployeeStoreImporter):
    pass

class EmployeeDepartmentImporter(BulkFromRattail, importing.model.EmployeeDepartmentImporter):
    pass

class EmployeeEmailAddressImporter(BulkFromRattail, importing.model.EmployeeEmailAddressImporter):
    pass

class EmployeePhoneNumberImporter(BulkFromRattail, importing.model.EmployeePhoneNumberImporter):
    pass

class ScheduledShiftImporter(BulkFromRattail, importing.model.ScheduledShiftImporter):
    pass

class WorkedShiftImporter(BulkFromRattail, importing.model.WorkedShiftImporter):
    pass

class CustomerImporter(BulkFromRattail, importing.model.CustomerImporter):
    pass

class CustomerGroupImporter(BulkFromRattail, importing.model.CustomerGroupImporter):
    pass

class CustomerGroupAssignmentImporter(BulkFromRattail, importing.model.CustomerGroupAssignmentImporter):
    pass

class CustomerPersonImporter(BulkFromRattail, importing.model.CustomerPersonImporter):
    pass

class CustomerEmailAddressImporter(BulkFromRattail, importing.model.CustomerEmailAddressImporter):
    pass

class CustomerPhoneNumberImporter(BulkFromRattail, importing.model.CustomerPhoneNumberImporter):
    pass

class VendorImporter(BulkFromRattail, importing.model.VendorImporter):
    pass

class VendorEmailAddressImporter(BulkFromRattail, importing.model.VendorEmailAddressImporter):
    pass

class VendorPhoneNumberImporter(BulkFromRattail, importing.model.VendorPhoneNumberImporter):
    pass

class VendorContactImporter(BulkFromRattail, importing.model.VendorContactImporter):
    pass

class DepartmentImporter(BulkFromRattail, importing.model.DepartmentImporter):
    pass

class SubdepartmentImporter(BulkFromRattail, importing.model.SubdepartmentImporter):
    pass

class CategoryImporter(BulkFromRattail, importing.model.CategoryImporter):
    pass

class FamilyImporter(BulkFromRattail, importing.model.FamilyImporter):
    pass

class ReportCodeImporter(BulkFromRattail, importing.model.ReportCodeImporter):
    pass

class DepositLinkImporter(BulkFromRattail, importing.model.DepositLinkImporter):
    pass

class TaxImporter(BulkFromRattail, importing.model.TaxImporter):
    pass

class BrandImporter(BulkFromRattail, importing.model.BrandImporter):
    pass


class ProductImporter(BulkFromRattail, importing.model.ProductImporter):
    """
    Product data requires some extra handling currently.  The bulk importer
    does not support the regular/current price foreign key fields, so those
    must be populated in some other way after the initial bulk import.
    """

    @property
    def simple_fields(self):
        fields = super(ProductImporter, self).simple_fields
        fields.remove('regular_price_uuid')
        fields.remove('current_price_uuid')
        return fields


class ProductCodeImporter(BulkFromRattail, importing.model.ProductCodeImporter):
    pass

class ProductCostImporter(BulkFromRattail, importing.model.ProductCostImporter):
    pass

class ProductPriceImporter(BulkFromRattail, importing.model.ProductPriceImporter):
    pass
