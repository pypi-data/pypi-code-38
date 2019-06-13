# -*- coding: utf-8; -*-
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
Rattail -> Rattail "versions" data import
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy_continuum as continuum

from rattail.db import model
from rattail.db.continuum import versioning_manager
from rattail.importing.rattail import FromRattailHandler, ToRattailHandler, FromRattail
from rattail.importing.model import ToRattail
from rattail.util import OrderedDict


class FromRattailToRattailVersions(FromRattailHandler, ToRattailHandler):
    """
    Handler for Rattail -> Rattail "versions" data import
    """
    local_title = "Rattail (Versions)"

    def get_importers(self):
        importers = OrderedDict()
        importers['Person'] = PersonImporter
        importers['PersonPhoneNumber'] = PersonPhoneNumberImporter
        importers['PersonEmailAddress'] = PersonEmailAddressImporter
        importers['PersonMailingAddress'] = PersonMailingAddressImporter
        importers['PersonNote'] = PersonNoteImporter
        importers['Role'] = RoleImporter
        # importers['Permission'] = PermissionImporter
        importers['User'] = UserImporter
        importers['UserRole'] = UserRoleImporter
        importers['Store'] = StoreImporter
        importers['StorePhoneNumber'] = StorePhoneNumberImporter
        importers['StoreEmailAddress'] = StoreEmailAddressImporter
        importers['Customer'] = CustomerImporter
        importers['CustomerPhoneNumber'] = CustomerPhoneNumberImporter
        importers['CustomerEmailAddress'] = CustomerEmailAddressImporter
        importers['CustomerMailingAddress'] = CustomerMailingAddressImporter
        importers['CustomerPerson'] = CustomerPersonImporter
        importers['CustomerGroup'] = CustomerGroupImporter
        importers['CustomerGroupAssignment'] = CustomerGroupAssignmentImporter
        importers['Employee'] = EmployeeImporter
        importers['EmployeePhoneNumber'] = EmployeePhoneNumberImporter
        importers['EmployeeEmailAddress'] = EmployeeEmailAddressImporter
        importers['EmployeeStore'] = EmployeeStoreImporter
        importers['EmployeeDepartment'] = EmployeeDepartmentImporter
        importers['EmployeeHistory'] = EmployeeHistoryImporter
        importers['WorkedShift'] = WorkedShiftImporter
        importers['Vendor'] = VendorImporter
        importers['VendorPhoneNumber'] = VendorPhoneNumberImporter
        importers['VendorEmailAddress'] = VendorEmailAddressImporter
        importers['VendorContact'] = VendorContactImporter
        importers['Department'] = DepartmentImporter
        importers['Subdepartment'] = SubdepartmentImporter
        importers['Category'] = CategoryImporter
        importers['Family'] = FamilyImporter
        importers['ReportCode'] = ReportCodeImporter
        importers['DepositLink'] = DepositLinkImporter
        importers['Brand'] = BrandImporter
        importers['Tax'] = TaxImporter
        importers['Product'] = ProductImporter
        importers['ProductCode'] = ProductCodeImporter
        importers['ProductCost'] = ProductCostImporter
        importers['ProductPrice'] = ProductPriceImporter
        importers['LabelProfile'] = LabelProfileImporter
        return importers

    def begin_local_transaction(self):
        super(FromRattailToRattailVersions, self).begin_local_transaction()
        self.uow = versioning_manager.unit_of_work(self.session)
        self.transaction = self.uow.create_transaction(self.session)
        if self.comment:
            self.transaction.meta = {'comment': self.comment}

    def get_importer_kwargs(self, key, **kwargs):
        kwargs = super(FromRattailToRattailVersions, self).get_importer_kwargs(key, **kwargs)
        kwargs['transaction'] = self.transaction
        return kwargs


class VersionImporter(FromRattail, ToRattail):
    """
    Base class for version model importers
    """

    def get_model_class(self):
        return continuum.version_class(self.host_model_class)

    @property
    def simple_fields(self):
        fields = super(VersionImporter, self).simple_fields
        fields.remove('operation_type')
        fields.remove('transaction_id')
        fields.remove('end_transaction_id')
        return fields

    def cache_query(self):
        return self.session.query(self.model_class)\
                           .filter(self.model_class.end_transaction_id == None)\
                           .filter(self.model_class.operation_type != continuum.Operation.DELETE)

    def normalize_local_object(self, obj):
        data = super(VersionImporter, self).normalize_local_object(obj)
        # cache local (version) object, for updating end_transaction_id
        # (note that this is called for host side as well, hence check)
        if isinstance(obj, self.model_class):
            data['_object'] = obj
        return data

    def make_version(self, host_data, operation_type):
        key = self.get_key(host_data)
        with self.session.no_autoflush:
            version = self.new_object(key)
            self.populate(version, host_data)
            version.transaction = self.transaction
            version.operation_type = operation_type
            self.session.add(version)
            return version

    def populate(self, obj, data):
        for field in self.simple_fields:
            if field not in self.key and field in data and field in self.fields:
                setattr(obj, field, data[field])

    def create_object(self, key, host_data):
        return self.make_version(host_data, continuum.Operation.INSERT)

    def update_object(self, obj, host_data, local_data=None, **kwargs):
        last_version = local_data.pop('_object')
        last_version.end_transaction_id = self.transaction.id
        return self.make_version(host_data, continuum.Operation.UPDATE)
    

class PersonImporter(VersionImporter):
    host_model_class = model.Person

class PersonPhoneNumberImporter(VersionImporter):
    host_model_class = model.PersonPhoneNumber

class PersonEmailAddressImporter(VersionImporter):
    host_model_class = model.PersonEmailAddress

class PersonMailingAddressImporter(VersionImporter):
    host_model_class = model.PersonMailingAddress

class PersonNoteImporter(VersionImporter):
    host_model_class = model.PersonNote

class RoleImporter(VersionImporter):
    host_model_class = model.Role

# class PermissionImporter(VersionImporter):
#     host_model_class = model.Permission

class UserImporter(VersionImporter):
    host_model_class = model.User

class UserRoleImporter(VersionImporter):
    host_model_class = model.UserRole

class StoreImporter(VersionImporter):
    host_model_class = model.Store

class StorePhoneNumberImporter(VersionImporter):
    host_model_class = model.StorePhoneNumber

class StoreEmailAddressImporter(VersionImporter):
    host_model_class = model.StoreEmailAddress

class CustomerImporter(VersionImporter):
    host_model_class = model.Customer

class CustomerPhoneNumberImporter(VersionImporter):
    host_model_class = model.CustomerPhoneNumber

class CustomerEmailAddressImporter(VersionImporter):
    host_model_class = model.CustomerEmailAddress

class CustomerMailingAddressImporter(VersionImporter):
    host_model_class = model.CustomerMailingAddress

class CustomerPersonImporter(VersionImporter):
    host_model_class = model.CustomerPerson

class CustomerGroupImporter(VersionImporter):
    host_model_class = model.CustomerGroup

class CustomerGroupAssignmentImporter(VersionImporter):
    host_model_class = model.CustomerGroupAssignment

class EmployeeImporter(VersionImporter):
    host_model_class = model.Employee

class EmployeePhoneNumberImporter(VersionImporter):
    host_model_class = model.EmployeePhoneNumber

class EmployeeEmailAddressImporter(VersionImporter):
    host_model_class = model.EmployeeEmailAddress

class EmployeeStoreImporter(VersionImporter):
    host_model_class = model.EmployeeStore

class EmployeeDepartmentImporter(VersionImporter):
    host_model_class = model.EmployeeDepartment

class EmployeeHistoryImporter(VersionImporter):
    host_model_class = model.EmployeeHistory

class WorkedShiftImporter(VersionImporter):
    host_model_class = model.WorkedShift

class VendorImporter(VersionImporter):
    host_model_class = model.Vendor

class VendorPhoneNumberImporter(VersionImporter):
    host_model_class = model.VendorPhoneNumber

class VendorEmailAddressImporter(VersionImporter):
    host_model_class = model.VendorEmailAddress

class VendorContactImporter(VersionImporter):
    host_model_class = model.VendorContact

class DepartmentImporter(VersionImporter):
    host_model_class = model.Department

class SubdepartmentImporter(VersionImporter):
    host_model_class = model.Subdepartment

class CategoryImporter(VersionImporter):
    host_model_class = model.Category

class FamilyImporter(VersionImporter):
    host_model_class = model.Family

class ReportCodeImporter(VersionImporter):
    host_model_class = model.ReportCode

class DepositLinkImporter(VersionImporter):
    host_model_class = model.DepositLink

class BrandImporter(VersionImporter):
    host_model_class = model.Brand

class TaxImporter(VersionImporter):
    host_model_class = model.Tax

class ProductImporter(VersionImporter):
    host_model_class = model.Product

class ProductCodeImporter(VersionImporter):
    host_model_class = model.ProductCode

class ProductCostImporter(VersionImporter):
    host_model_class = model.ProductCost

class ProductPriceImporter(VersionImporter):
    host_model_class = model.ProductPrice

class LabelProfileImporter(VersionImporter):
    host_model_class = model.LabelProfile
