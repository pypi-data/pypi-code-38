# This file is part of Sympathy for Data.
# Copyright (c) 2015-2016 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import base64
import json
import sys

import Gui.application
import Gui.flow.functions
import Gui.datatypes
import Gui.execore
from sympathy.platform import version_support as vs


class ExtractLambdaSubprocess(object):
    _marker = '__SY_EXTRACT_OUTPUT_MARKER__'

    def _lambdas_from_flow(self, flow):
        return Gui.flow.functions.top_lambdas_from_flow(flow)

    def execute(self, json_data, datatype, filenames, **kwargs):
        vs.wrap_encode_std()
        data = json.loads(base64.b64decode(json_data).decode('ascii'))
        env = data['env']
        lib = data['lib']
        folders = data['folders']
        identifier = data['identifier']

        datatype = Gui.datatypes.DataType.from_str(datatype)

        extract_results = Gui.application.extract_lambdas(
            filenames, datatype, env, lib, folders, identifier)

        results = []

        for filename, result in extract_results:
            status, flow_or_error = result
            if status:
                flow = flow_or_error
                lambdas = []
                flowdata = []
                try:
                    top_lambdas = self._lambdas_from_flow(flow)
                    lambdas.extend(
                        Gui.flow.functions.filter_lambdas_datatype(
                            top_lambdas, datatype))

                    for lambda_ in lambdas:
                        flowdata.append(json.loads(
                            Gui.execore.flowdata(lambda_)[
                                'parameters']['data']['flow']['value']))
                except:
                    result = (False, 'Could not extract lambdas due to error')
                else:
                    result = (True, flowdata)

            results.append((filename, result))

        sys.stdout.write(self._marker)
        sys.stdout.write(
            base64.b64encode(json.dumps(results).encode('ascii')).decode(
                'ascii'))


class ExtractFlowSubprocess(ExtractLambdaSubprocess):
    def _lambdas_from_flow(self, flow):
        return Gui.flow.functions.flow_to_lambda(flow)
