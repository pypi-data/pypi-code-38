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
# Copyright 2019 SerialLab Corp.  All rights reserved.
import traceback
import logging
import uuid
from rest_framework import status
from rest_framework.response import Response
from EPCPyYes.core.v1_2 import helpers
from quartet_epcis.db_api.queries import EPCISDBProxy
from quartet_epcis.models import events, entries, headers

class RocItQuery():

    def __init__(self):
        pass

    @staticmethod
    def RetrievePackagingHierarchy(tag_id, send_children, send_product_info):

        parent_tag = ""
        product = ""
        lot = ""
        uom=""
        expiry = ""
        status = ""
        state = ""
        document_id = ""
        document_type = ""
        child_tag_count = 0
        child_tags = []
        send_product_info = (send_product_info is not None and send_product_info.lower() == 'true')
        send_children = (send_children is not None and send_children.lower() == 'true')

        # Create the DBProxy
        query = EPCISDBProxy()
        # Get the entry, then get the last Event the entry participated in.
        entry = query.get_entries_by_epcs(epcs=[tag_id])[0]
        last_event = entry.last_event

        if last_event is not None:
            # If there was a last_event, then get the bizStep (state in the response)
            # And disposition (status in the response)
            try:
                state = last_event.biz_step.split(':')[4]
            except:
                raise Exception('Invalid CBV bizStep urn found.')
            try:
                status = last_event.disposition.split(':')[4]
            except:
                # disposition may not have been sent in the EPCIS Doc, ignore
                pass

        if send_children:
            # The request is to return the children.
            try:
                # get the children of tag_id
                children = query.get_epcs_by_parent_identifier(identifier=tag_id, select_for_update=True)
                # get the count of the children
                child_tag_count = len(children)
                # build the child_tags array witht he children of tag_id
                for child in children:
                    child_tags.append(child)
                    # "urn:epc:id:sgtin:305555.3555555.1"
                    if(str(child).find('sgtin') > 0):
                        gtin = child.split(':')
                        gtin = gtin[4].split('.')
                        cp = gtin[0][2:]
                        ir = gtin[1][1:]
                        product = "{0}{1}".format(cp, ir)
            except entries.Entry.DoesNotExist:
                # No Children found. This can be ignored.
                pass

        if send_product_info:
            events = query.get_events_by_entry_identifer(entry_identifier=tag_id)
            for event in events:
                ilmds = query.get_ilmd(db_event=event.event)
                for ilmd in ilmds:
                    if ilmd.name == 'itemExpirationDate':
                      expiry = ilmd.value
                    elif ilmd.name == 'lotNumber':
                      lot = ilmd.value

                if len(lot) > 0 and len(expiry) > 0:
                    break
        ret_val = {
                    "msg_id": uuid.uuid1(),
                    "tag_id": tag_id,
                    "parent_tag": parent_tag,
                    "status": status.upper(),
                    "state": state.upper(),
                    "child_tag_count": child_tag_count,
                    "child_tags": child_tags,
                    "document_id":document_id,
                    "document_type":document_type,
                    "expiry": expiry,
                    "lot": lot,
                    "uom": uom,
                    "product": product
                }

        return ret_val
