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
import json

from EPCPyYes.core.v1_2 import json_decoders, events as yes_events
from quartet_epcis.models import headers, events
from quartet_epcis.parsing.business_parser import BusinessEPCISParser


class JSONParser(BusinessEPCISParser):

    def parse(self):
        self._message = headers.Message()
        self._message.save()
        if self.stream.startswith('/'):
            with open(self.stream, 'r') as f:
                self.stream = f.read()
        jsonobj = json.loads(self.stream)
        events = jsonobj.get('events', [])
        if len(events) == 0:
            raise self.NoEventsError('There were no events in the inbound'
                                     ' JSON file.')
        for event in events:
            if 'objectEvent' in event:
                decoder = json_decoders.ObjectEventDecoder(event)
                self.handle_object_event(decoder.get_event())
            elif 'aggregationEvent' in event:
                decoder = json_decoders.AggregationEventDecoder(event)
                self.handle_aggregation_event(decoder.get_event())
            elif 'transactionEvent' in event:
                decoder = json_decoders.TransactionEventDecoder(event)
                self.handle_transaction_event(decoder.get_event())
            else:
                raise self.InvalidEventError('The JSON parser encountered an'
                                             ' event that could not be parsed'
                                             ' %s' % str(event))
        self.clear_cache()
        return self._message.id

    class NoEventsError(Exception):
        pass

    class InvalidEventError(Exception):
        pass
