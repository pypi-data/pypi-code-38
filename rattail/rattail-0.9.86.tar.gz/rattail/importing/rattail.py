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
Rattail -> Rattail data import
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import Session
from rattail.importing import model
from rattail.importing.handlers import FromSQLAlchemyHandler, ToSQLAlchemyHandler
from rattail.importing.sqlalchemy import FromSQLAlchemy
from rattail.util import OrderedDict


class FromRattailHandler(FromSQLAlchemyHandler):
    """
    Base class for import handlers which target a Rattail database on the local side.
    """
    host_title = "Rattail"

    def make_host_session(self):
        return Session()


class ToRattailHandler(ToSQLAlchemyHandler):
    """
    Base class for import handlers which target a Rattail database on the local side.
    """
    local_title = "Rattail"

    def make_session(self):
        kwargs = {}
        if hasattr(self, 'runas_user'):
            kwargs['continuum_user'] = self.runas_user
        return Session(**kwargs)

    def begin_local_transaction(self):
        self.session = self.make_session()
        if hasattr(self, 'runas_username') and self.runas_username:
            self.session.set_continuum_user(self.runas_username)


class FromRattailToRattailBase(object):
    """
    Common base class for Rattail -> Rattail data import/export handlers.
    """

    def get_importers(self):
        importers = OrderedDict()
        importers['Person'] = PersonImporter
        importers['PersonEmailAddress'] = PersonEmailAddressImporter
        importers['PersonPhoneNumber'] = PersonPhoneNumberImporter
        importers['PersonMailingAddress'] = PersonMailingAddressImporter
        importers['User'] = UserImporter
        importers['AdminUser'] = AdminUserImporter
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
        importers['Member'] = MemberImporter
        importers['MemberEmailAddress'] = MemberEmailAddressImporter
        importers['MemberPhoneNumber'] = MemberPhoneNumberImporter
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
        importers['InventoryAdjustmentReason'] = InventoryAdjustmentReasonImporter
        importers['Brand'] = BrandImporter
        importers['Product'] = ProductImporter
        importers['ProductCode'] = ProductCodeImporter
        importers['ProductCost'] = ProductCostImporter
        importers['ProductPrice'] = ProductPriceImporter
        importers['ProductStoreInfo'] = ProductStoreInfoImporter
        importers['ProductVolatile'] = ProductVolatileImporter
        importers['ProductImage'] = ProductImageImporter
        importers['LabelProfile'] = LabelProfileImporter
        return importers

    def get_default_keys(self):
        keys = self.get_importer_keys()
        if 'AdminUser' in keys:
            keys.remove('AdminUser')
        if 'ProductImage' in keys:
            keys.remove('ProductImage')
        return keys


class FromRattailToRattailImport(FromRattailToRattailBase, FromRattailHandler, ToRattailHandler):
    """
    Handler for Rattail (other) -> Rattail (local) data import.

    .. attribute:: direction

       Value is ``'import'`` - see also
       :attr:`rattail.importing.handlers.ImportHandler.direction`.
    """
    dbkey = 'host'

    @property
    def host_title(self):
        return "{} ({})".format(self.config.app_title(default="Rattail"), self.dbkey)

    @property
    def local_title(self):
        return self.config.node_title()

    def make_host_session(self):
        return Session(bind=self.config.rattail_engines[self.dbkey])


class FromRattailToRattailExport(FromRattailToRattailBase, FromRattailHandler, ToRattailHandler):
    """
    Handler for Rattail (local) -> Rattail (other) data export.

    .. attribute:: direction

       Value is ``'export'`` - see also
       :attr:`rattail.importing.handlers.ImportHandler.direction`.
    """
    direction = 'export'

    @property
    def host_title(self):
        return self.config.node_title()

    @property
    def local_title(self):
        return "{} ({})".format(self.config.app_title(default="Rattail"), self.dbkey)

    def make_session(self):
        return Session(bind=self.config.rattail_engines[self.dbkey])


class FromRattail(FromSQLAlchemy):
    """
    Base class for Rattail -> Rattail data importers.
    """

    @property
    def host_model_class(self):
        return self.model_class

    @property
    def supported_fields(self):
        """
        We only need to support the simple fields in a Rattail->Rattail import,
        since all relevant tables should be covered and therefore no need to do
        crazy foreign key acrobatics etc.
        """
        return self.simple_fields

    def query(self):
        """
        Leverage the same caching optimizations on both sides, if applicable.
        """
        query = super(FromRattail, self).query()
        if hasattr(self, 'cache_query_options'):
            options = self.cache_query_options()
            if options:
                for option in options:
                    query = query.options(option)
        return query

    def normalize_host_object(self, obj):
        """
        Normalization should work the same for both sides.
        """
        return self.normalize_local_object(obj)


class PersonImporter(FromRattail, model.PersonImporter):
    pass

class PersonEmailAddressImporter(FromRattail, model.PersonEmailAddressImporter):
    pass

class PersonPhoneNumberImporter(FromRattail, model.PersonPhoneNumberImporter):
    pass

class PersonMailingAddressImporter(FromRattail, model.PersonMailingAddressImporter):
    pass

class UserImporter(FromRattail, model.UserImporter):
    pass

class AdminUserImporter(FromRattail, model.AdminUserImporter):

    @property
    def supported_fields(self):
        return super(AdminUserImporter, self).supported_fields + [
            'admin',
        ]

    def normalize_host_object(self, user):
        data = super(AdminUserImporter, self).normalize_local_object(user) # sic
        if 'admin' in self.fields: # TODO: do we really need this, after the above?
            data['admin'] = self.admin_uuid in [r.role_uuid for r in user._roles]
        return data


class MessageImporter(FromRattail, model.MessageImporter):
    pass

class MessageRecipientImporter(FromRattail, model.MessageRecipientImporter):
    pass

class StoreImporter(FromRattail, model.StoreImporter):
    pass

class StorePhoneNumberImporter(FromRattail, model.StorePhoneNumberImporter):
    pass

class EmployeeImporter(FromRattail, model.EmployeeImporter):
    pass

class EmployeeStoreImporter(FromRattail, model.EmployeeStoreImporter):
    pass

class EmployeeDepartmentImporter(FromRattail, model.EmployeeDepartmentImporter):
    pass

class EmployeeEmailAddressImporter(FromRattail, model.EmployeeEmailAddressImporter):
    pass

class EmployeePhoneNumberImporter(FromRattail, model.EmployeePhoneNumberImporter):
    pass

class ScheduledShiftImporter(FromRattail, model.ScheduledShiftImporter):
    pass

class WorkedShiftImporter(FromRattail, model.WorkedShiftImporter):
    pass

class CustomerImporter(FromRattail, model.CustomerImporter):
    pass

class CustomerGroupImporter(FromRattail, model.CustomerGroupImporter):
    pass

class CustomerGroupAssignmentImporter(FromRattail, model.CustomerGroupAssignmentImporter):
    pass

class CustomerPersonImporter(FromRattail, model.CustomerPersonImporter):
    pass

class CustomerEmailAddressImporter(FromRattail, model.CustomerEmailAddressImporter):
    pass

class CustomerPhoneNumberImporter(FromRattail, model.CustomerPhoneNumberImporter):
    pass

class MemberImporter(FromRattail, model.MemberImporter):
    pass

class MemberEmailAddressImporter(FromRattail, model.MemberEmailAddressImporter):
    pass

class MemberPhoneNumberImporter(FromRattail, model.MemberPhoneNumberImporter):
    pass

class VendorImporter(FromRattail, model.VendorImporter):
    pass

class VendorEmailAddressImporter(FromRattail, model.VendorEmailAddressImporter):
    pass

class VendorPhoneNumberImporter(FromRattail, model.VendorPhoneNumberImporter):
    pass

class VendorContactImporter(FromRattail, model.VendorContactImporter):
    pass

class DepartmentImporter(FromRattail, model.DepartmentImporter):
    pass

class SubdepartmentImporter(FromRattail, model.SubdepartmentImporter):
    pass

class CategoryImporter(FromRattail, model.CategoryImporter):
    pass

class FamilyImporter(FromRattail, model.FamilyImporter):
    pass

class ReportCodeImporter(FromRattail, model.ReportCodeImporter):
    pass

class DepositLinkImporter(FromRattail, model.DepositLinkImporter):
    pass

class TaxImporter(FromRattail, model.TaxImporter):
    pass

class InventoryAdjustmentReasonImporter(FromRattail, model.InventoryAdjustmentReasonImporter):
    pass

class BrandImporter(FromRattail, model.BrandImporter):
    pass

class ProductImporter(FromRattail, model.ProductImporter):

    # TODO...
    @property
    def simple_fields(self):
        fields = super(ProductImporter, self).simple_fields
        fields.remove('regular_price_uuid')
        fields.remove('current_price_uuid')
        return fields

    def query(self):
        query = super(ProductImporter, self).query()

        # make sure potential unit items (i.e. rows with NULL unit_uuid) come
        # first, so they will be created before pack items reference them
        # cf. https://www.postgresql.org/docs/current/static/queries-order.html
        # cf. https://stackoverflow.com/a/7622046
        query = query.order_by(self.host_model_class.unit_uuid.desc())

        return query


class ProductCodeImporter(FromRattail, model.ProductCodeImporter):
    pass

class ProductCostImporter(FromRattail, model.ProductCostImporter):
    pass

class ProductPriceImporter(FromRattail, model.ProductPriceImporter):

    @property
    def supported_fields(self):
        return super(ProductPriceImporter, self).supported_fields + self.product_reference_fields


class ProductStoreInfoImporter(FromRattail, model.ProductStoreInfoImporter):
    pass

class ProductVolatileImporter(FromRattail, model.ProductVolatileImporter):
    pass


class ProductImageImporter(FromRattail, model.ProductImageImporter):
    """
    Importer for product images.  Note that this uses the "batch" approach
    because fetching all data up front is not performant when the host/local
    systems are on different machines etc.
    """

    def query(self):
        query = self.host_session.query(self.model_class)\
                                 .order_by(self.model_class.uuid)
        return query[self.host_index:self.host_index + self.batch_size]


class LabelProfileImporter(FromRattail, model.LabelProfileImporter):

    def query(self):
        query = super(LabelProfileImporter, self).query()

        if not self.config.getbool('rattail', 'labels.sync_all_profiles', default=False):
            # only fetch labels from host which are marked as "sync me"
            query = query .filter(self.model_class.sync_me == True)

        return query.order_by(self.model_class.ordinal)
