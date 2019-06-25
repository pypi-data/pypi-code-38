# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.


from rest_framework.routers import DefaultRouter
from quartet_epcis import viewsets


router = DefaultRouter()
router.register(r'entries', viewsets.EntryViewSet, base_name='entries')
router.register(r'entry-events', viewsets.EntryEventViewSet,
                base_name='entry-events')
router.register(r'events', viewsets.EventViewSet, base_name='events')
router.register(r'transformation-ids', viewsets.TransformationIDViewSet,
                base_name='transformation-ids')
router.register(r'error-declarations', viewsets.ErrorDeclarationViewSet,
                base_name='error-declarations')
router.register(r'quantity-elements', viewsets.QuantityElementViewSet,
                base_name='quantity-elements')
router.register(r'business-transactions', viewsets.BusinessTransactionViewSet,
                base_name='business-transactions')
router.register(r'ilmd', viewsets.InstanceLotMasterDataViewSet,
                base_name='ilmd')
router.register(r'sources', viewsets.SourceViewSet, base_name='sources')
router.register(r'source-events', viewsets.SourceEventViewSet,
                base_name='source-events')
router.register(r'destinations', viewsets.DestinationViewSet,
                base_name='destinations')
router.register(r'destination-event', viewsets.DestinationEventViewSet,
                base_name='destinations')
router.register(r'messages',viewsets.MessageViewSet, base_name='messages')
