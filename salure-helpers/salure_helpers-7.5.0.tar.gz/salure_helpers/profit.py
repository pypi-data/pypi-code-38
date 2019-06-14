import json
import time
import requests


class GetConnector:

    def __init__(self,  environment, base64token, base_url='rest.afas.online'):
        self.environment = environment
        self.base64token = base64token
        self.base_url = base_url

    def get_metadata(self):
        url = 'https://{}.{}/profitrestservices/metainfo'.format(self.environment, self.base_url)
        authorizationHeader = {'Authorization': 'AfasToken ' + self.base64token}
        vResponse = requests.get(url, headers=authorizationHeader).json()['getConnectors']

        return vResponse
        # for key in vResponse:
        #     if len(key['id']) > 0:
        #         self.get_data(key['id'])

    def get_data(self, connector):
        start = time.time()

        total_response = []
        loop_boolean = True
        no_of_loops = 0
        no_of_results = 0

        while loop_boolean:
            url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, connector)
            parameters = { "skip": 40000 * no_of_loops, "take": 40000}
            authorization_header = {'Authorization': 'AfasToken {}'.format(self.base64token)}
            response = requests.get(url.encode("utf-8"), parameters, headers=authorization_header)
            if response.status_code == 200:
                response_json = response.json()['rows']
                no_of_loops += 1
                no_of_results += len(response_json)
                loop_boolean = True if len(response_json) == 40000 else False

                print(time.strftime('%H:%M:%S'), 'Got next connector from profit: ',connector, ' With nr of rows: ', no_of_results)
                total_response += response_json
            else:
                return response.text

        return total_response

    def get_filtered_data(self, connector, fields=None, values=None, operators=None):
        # possible operators are: [1:=, 2:>=, 3:<=, 4:>, 5:<, 6:exists, 7:!=, 8:isEmpty, 9:notEmpty]
        # for AND filter, use ',' between fields and values, for OR filter, use ';'

        total_response = []
        loop_boolean = True
        no_of_loops = 0
        no_of_results = 0


        if fields != None:
            parameters = {"filterfieldids": fields, "filtervalues": values, "operatortypes": operators}
        else:
            parameters = {}

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, connector)

        while loop_boolean:
            loop_parameters = {"skip": 40000 * no_of_loops, "take": 40000}
            parameters.update(loop_parameters)
            authorization_header = {'Authorization': 'AfasToken {}'.format(self.base64token)}
            response = requests.get(url.encode("utf-8"), parameters, headers=authorization_header)
            if response.status_code == 200:
                response_json = response.json()['rows']
                no_of_loops += 1
                no_of_results += len(response_json)
                loop_boolean = True if len(response_json) == 40000 else False

                print(time.strftime('%H:%M:%S'), 'Got next connector from profit: ', connector, ' With nr of rows: ', no_of_results)
                total_response += response_json
            else:
                return response.text

        return total_response


class UpdateConnector:

    def __init__(self, environment, base64token, base_url='rest.afas.online'):
        self.environment = environment
        self.base64token = base64token
        self.base_url = base_url

    def update(self, updateconnector, data):
        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, updateconnector)

        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        update = requests.request("PUT", url, data=data, headers=headers)

        return update

    def update_person(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['employee_id', 'mail_work', 'mail_private', 'mobile_work', 'mobile_private', 'nickname', 'first_name', 'initials', 'prefix', 'last_name',
                          'birth_name', 'gender', 'nationality', 'birth_date', 'country_of_birth', 'ssn', 'marital_status', 'date_of_marriage', 'phone_work', 'phone_private']
        required_fields = ['employee_id', 'person_id']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Pietertje, field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Pietertje, field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/KnPerson')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "KnPerson": {
                            "Element": {
                                "Fields": {
                                    "MatchPer": "0",
                                    "BcCo": data['person_id']
                                }
                            }
                        }
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"EmA": data['mail_work']}) if 'mail_work' in data else fields_to_update
        fields_to_update.update({"EmA2": data['mail_private']}) if 'mail_private' in data else fields_to_update
        fields_to_update.update({"MbNr": data['mobile_work']}) if 'mobile_work' in data else fields_to_update
        fields_to_update.update({"MbN2": data['mobile_private']}) if 'mobile_private' in data else fields_to_update
        fields_to_update.update({"CaNm": data['nickname']}) if 'nickname' in data else fields_to_update
        fields_to_update.update({"FiNm": data['first_name']}) if 'first_name' in data else fields_to_update
        fields_to_update.update({"In": data['initials']}) if 'initials' in data else fields_to_update
        fields_to_update.update({"Is": data['prefix']}) if 'prefix' in data else fields_to_update
        fields_to_update.update({"LaNm": data['last_name']}) if 'last_name' in data else fields_to_update
        fields_to_update.update({"NmBi": data['birth_name']}) if 'birth_name' in data else fields_to_update
        fields_to_update.update({"ViGe": data['gender']}) if 'gender' in data else fields_to_update
        fields_to_update.update({"PsNa": data['nationality']}) if 'nationality' in data else fields_to_update
        fields_to_update.update({"DaBi": data['birth_date']}) if 'birth_date' in data else fields_to_update
        fields_to_update.update({"RsBi": data['country_of_birth']}) if 'country_of_birth' in data else fields_to_update
        fields_to_update.update({"SoSe": data['ssn']}) if 'ssn' in data else fields_to_update
        fields_to_update.update({"ViCs": data['marital_status']}) if 'marital_status' in data else fields_to_update
        fields_to_update.update({"DaMa": data['date_of_marriage']}) if 'date_of_marriage' in data else fields_to_update
        fields_to_update.update({"TeNr": data['phone_work']}) if 'phone_work' in data else fields_to_update
        fields_to_update.update({"TeN2": data['phone_private']}) if 'phone_private' in data else fields_to_update

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=headers)

        return update


    def update_address(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['street_number_add', 'city']
        required_fields = ['employee_id', 'person_id', 'country', 'street', 'street_number', 'postal_code', 'startdate']
        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Pietertje, field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Pietertje, field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/KnPerson')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "KnPerson": {
                            "Element": {
                                "Fields": {
                                    "MatchPer": "0",
                                    "BcCo": data['person_id']
                                },
                                "Objects": {
                                    "KnBasicAddressAdr": {
                                        "Element": {
                                            "Fields": {
                                                "CoId": data['country'],
                                                "PbAd": False,
                                                "Ad": data['street'],
                                                "HmNr": data['street_number'],
                                                "BcCo": data['employee_id'],
                                                "ZpCd": data['postal_code'],
                                                "ResZip": True,
                                                "BeginDate": data['startdate']
                                            }
                                        }
                                    },
                                    "KnBasicAddressPad": {
                                        "Element": {
                                            "Fields": {
                                                "CoId": data['country'],
                                                "PbAd": False,
                                                "Ad": data['street'],
                                                "HmNr": data['street_number'],
                                                "BcCo": data['employee_id'],
                                                "ZpCd": data['postal_code'],
                                                "ResZip": True,
                                                "BeginDate": data['startdate']
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"HmAd": data['street_number_add']}) if 'street_number_add' in data else fields_to_update
        fields_to_update.update({"Rs": data['city']}) if 'city' in data else fields_to_update

        # This is to include custom fields
        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Objects']['KnBasicAddressAdr']['Element']['Fields'].update(fields_to_update)
        base_body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Objects']['KnBasicAddressPad']['Element']['Fields'].update(fields_to_update)

        update = requests.request("POST", url, data=json.dumps(base_body), headers=headers)

        return update


    def update_contract(self, data: dict, overload_fields={}):
        """
        :param data: Dictionary of fields that you want to update in AFAS. Only fields listed in allowed arrays are accepted. Fields listed in required fields array, are mandatory
        :return: status code for request and optional error message
        """
        allowed_fields_contract = ['employee_id', 'type_of_employment', 'enddate_contract']
        required_fields_contract = ['employee_id', 'startdate_contract', 'cao', 'terms_of_employment', 'type_of_contract', 'employer_number', 'type_of_employee', 'employment']
        allowed_fields_function = ['costcarrier_id']
        required_fields_function = ['organizational_unit', 'function_id', 'costcenter_id']
        allowed_fields_timetable = ['changing_work_pattern']
        required_fields_timetable = ['weekly_hours', 'parttime_percentage']
        allowed_fields_salary = ['step']
        required_fields_salary = ['type_of_salary', 'salary_amount', 'period_table']
        allowed_fields = allowed_fields_contract + allowed_fields_salary + allowed_fields_timetable + allowed_fields_function
        required_fields = required_fields_contract + required_fields_function + required_fields_timetable + required_fields_salary

        # Check if there are fields that are not allowed or fields missing that are required
        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Pietertje, field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))
        for field in required_fields_contract:
            if field not in data.keys():
                return 'Pietertje, field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasContract')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
          "AfasEmployee": {
            "Element": {
              "@EmId": data['employee_id'],
              "Objects": {
                "AfasContract": {
                  "Element": {
                    "@DaBe": data['startdate_contract'],
                    "Fields": {
                      "ClId": data['cao'],
                      "WcId": data['terms_of_employment'],
                      "ApCo": data['type_of_contract'],
                      "CmId": data['employer_number'],
                      "EmMt": data['type_of_employee'],
                      "ViEt": data['employment']
                    }
                  }
                }
              }
            }
          }
        }

        # Extra JSON objects which are optional at contract creation
        function = {
            "AfasOrgunitFunction": {
                "Element": {
                    "@DaBe": data['startdate_contract'],
                    "Fields": {
                    }
                }
            }
        }

        timetable = {
            "AfasTimeTable": {
                "Element": {
                    "@DaBg": data['startdate_contract'],
                    "Fields": {
                        "StPa": True
                    }
                }
            }
        }

        salary = {
            "AfasSalary": {
                "Element": {
                    "@DaBe": data['startdate_contract'],
                    "Fields": {
                    }
                }
            }
        }

        # If one of the optional fields of a subelement is included, we need to merge the whole JSON object to the basebody
        if any(field in data.keys() for field in allowed_fields_function):
            for field in required_fields_function:
                if field not in data.keys():
                    return 'Pietertje, field {field} is required. Required fields for function are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

            fields_to_update = {}
            fields_to_update.update({"DpId": data['organizational_unit']}) if 'organizational_unit' in data else fields_to_update
            fields_to_update.update({"FuId": data['function_id']}) if 'function_id' in data else fields_to_update
            fields_to_update.update({"CcId": data['costcenter_id']}) if 'costcenter_id' in data else fields_to_update
            fields_to_update.update({"CrId": data['costcarrier_id']}) if 'costcarrier_id' in data else fields_to_update

            # merge subelement with basebody
            function['AfasOrgunitFunction']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(function)

        if any(field in data.keys() for field in allowed_fields_timetable):
            for field in required_fields_timetable:
                if field not in data.keys():
                    return 'Pietertje, field {field} is required. Required fields for timetable are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

            fields_to_update = {}
            fields_to_update.update({"StPa": data['changing_work_pattern']}) if 'changing_work_pattern' in data else fields_to_update
            fields_to_update.update({"HrWk": data['weekly_hours']}) if 'weekly_hours' in data else fields_to_update
            fields_to_update.update({"PcPt": data['parttime_percentage']}) if 'parttime_percentage' in data else fields_to_update

            timetable['AfasTimeTable']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(timetable)

        if any(field in data.keys() for field in allowed_fields_salary):
            for field in required_fields_salary:
                if field not in data.keys():
                    return 'Pietertje, field {field} is required. Required fields for salaries are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

            fields_to_update = {}
            fields_to_update.update({"SaSt": data['step']}) if 'step' in data else fields_to_update
            fields_to_update.update({"SaPe": data['type_of_salary']}) if 'type_of_salary' in data else fields_to_update
            fields_to_update.update({"EmSa": data['salary_amount']}) if 'salary_amount' in data else fields_to_update
            fields_to_update.update({"PtId": data['period_table']}) if 'period_table' in data else fields_to_update

            salary['AfasSalary']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(salary)

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update({"DaEn": data['enddate_contract']}) if 'enddate_contract' in data else fields_to_update
        fields_to_update.update({"PEmTy": data['type_of_employment']}) if 'type_of_employment' in data else fields_to_update

        # This is to include custom fields
        # TODO: implement overload for subelements too (eg. salary, function etc)
        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasContract']['Element']['Fields'].update(fields_to_update)

        update = requests.request("POST", url, data=json.dumps(base_body), headers=headers)

        return update


    def update_function(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['formation', 'costcarrier']
        required_fields = ['startdate', 'employee_id', 'organizational_unit', 'function', 'costcentre']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Pietertje, field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Pietertje, field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasOrgunitFunction')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
          "AfasEmployee": {
            "Element": {
              "@EmId": data['employee_id'],
              "Objects": {
                "AfasOrgunitFunction": {
                  "Element": {
                    "@DaBe": data['startdate'],
                    "Fields": {
                      "DpId": data['organizational_unit'],
                      "FuId": data['function'],
                      "CrId": data['costcentre']
                    }
                  }
                }
              }
            }
          }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"FpId": data['formation']}) if 'formation' in data else fields_to_update
        fields_to_update.update({"CcId": data['costcarrier']}) if 'costcarrier' in data else fields_to_update

        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasOrgunitFunction']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=headers)

        return update


    def update_salary(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['step', 'period_table', 'salary_year']
        required_fields = ['startdate', 'employee_id', 'salary_amount', 'salary_type']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Pietertje, field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Pietertje, field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasSalary')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
          "AfasEmployee": {
            "Element": {
              "@EmId": data['employee_id'],
              "Objects": {
                "AfasSalary": {
                  "Element": {
                    "@DaBe": data['startdate'],
                    "Fields": {
                        "SaPe": data['salary_type'],
                        "EmSa": data['salary_amount']
                    }
                  }
                }
              }
            }
          }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"SaSt": data['step']}) if 'step' in data else fields_to_update
        fields_to_update.update({"SaYe": data['salary_year']}) if 'salary_year' in data else fields_to_update
        fields_to_update.update({"PtId": data['period_table']}) if 'period_table' in data else fields_to_update.update({"PtId": 5})

        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasSalary']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=headers)

        return update

    def update_timetable(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """

        allowed_fields = ['changing_work_pattern']
        required_fields = ['startdate', 'employee_id', 'weekly_hours', 'parttime_percentage']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Pietertje, field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Pietertje, field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasTimeTable')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
          "AfasEmployee": {
            "Element": {
              "@EmId": data['employee_id'],
              "Objects": {
                "AfasTimeTable": {
                  "Element": {
                    "@DaBe": data['startdate'],
                    "Fields": {
                        "StPa": True,
                        "HrWk": data['weekly_hours'],
                        "PcPt": data['parttime_percentage']
                    }
                  }
                }
              }
            }
          }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"StPa": data['changing_work_pattern']}) if 'changing_work_pattern' in data else fields_to_update

        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasTimeTable']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=headers)

        return update

    def new_wage_mutation(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['period_table']
        required_fields = ['employee_id', 'year', 'month', 'employer_id', 'wage_component_id', 'value']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Pietertje, field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Pietertje, field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'HrCompMut')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
          "HrCompMut": {
            "Element": {
              "@Year": data['year'],
              "@PeId": data['month'],
              "@EmId": data['employee_id'],
              "@ErId": data['employer_id'],
              "@Sc02": data['wage_component_id'],
              "Fields": {
                "VaD1": data['value']
              }
            }
          }
        }
        fields_to_update = {}
        selector_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        selector_to_update.update({"@PtId": data['period_table']}) if 'period_table' in data else selector_to_update.update({"@PtId": 5})

        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['HrCompMut']['Element']['Fields'].update(fields_to_update)
        base_body['HrCompMut']['Element'].update(selector_to_update)

        update = requests.request("POST", url, data=json.dumps(base_body), headers=headers)

        return update

    def update_bank_account(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['bankname', 'country']
        required_fields = ['employee_id', 'bank_account', 'iban']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Pietertje, field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Pietertje, field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasBankInfo')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
          "AfasEmployee": {
            "Element": {
              "@EmId": data['employee_id'],
              "Objects": {
                "AfasBankInfo": {
                  "Element": {
                    "@AcId": data['bank_account'],  # "0417164300",
                    "@NoBk": False,                 # Cash payment (old)
                    "Fields": {
                      "IbCk": True,                 # IBAN check (always true)
                      "Iban": data['iban']          # "NL91ABNA0417164300"
                    }
                  }
                }
              }
            }
          }
        }

        fields_to_update = {}



        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"BkIc": data['bankname']}) if 'bankname' in data else fields_to_update
        fields_to_update.update({"CoId": data['country']}) if 'country' in data else fields_to_update

        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasBankInfo']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=headers)

        return update

    def new_employee_with_first_contract(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Any custom fields that are not in the allowed or required fields
        :return: status code for request and optional error message
        """

        allowed_fields_person = ['first_name', 'place_of_birth', 'date_of_birth', 'country', 'email_work', 'email_home', 'ssn']
        required_fields_person = ['employee_id', 'last_name', 'gender']
        required_fields_contract = ['date_effective', 'type_of_contract', 'collective_agreement', 'employment_conditions', 'employment', 'type_of_employee', 'employer']
        required_fields_address = ['house_number', 'street', 'postal_code', 'city']
        required_fields_function = ['organizational_unit', 'date_effective', 'function_id', 'costcenter']
        required_fields_schedule = ['weekly_hours', 'parttime_percentage']
        required_fields_salary = ['type_of_salary', 'amount']

        allowed_fields = allowed_fields_person
        required_fields = required_fields_contract + required_fields_function + required_fields_schedule + required_fields_salary + required_fields_address + required_fields_person

        # Check if there are fields that are not allowed or fields missing that are required
        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Pietertje, field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))
        for field in required_fields:
            if field not in data.keys():
                return 'Pietertje, field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_ID'],  # Employee selector
                    "Objects": {
                        "KnPerson": {
                            "Element": {
                                "Fields": {
                                    "PadAdr": False,                # Postbus adres
                                    "AutoNum": False,               # Autonumber
                                    # Match existing employees on BSN [{"id":"0","description":"Zoek op BcCo (Persoons-ID)"},{"id":"1","description":"Burgerservicenummer"},{"id":"2","description":"Naam + voorvoegsel + initialen + geslacht"},{"id":"3","description":"Naam + voorvoegsel + initialen + geslacht + e-mail werk"},{"id":"4","description":"Naam + voorvoegsel + initialen + geslacht + mobiel werk"},{"id":"5","description":"Naam + voorvoegsel + initialen + geslacht + telefoon werk"},{"id":"6","description":"Naam + voorvoegsel + initialen + geslacht + geboortedatum"},{"id":"7","description":"Altijd nieuw toevoegen"}]
                                    "MatchPer": "1",
                                    "BcCo": data['employee_ID'],    # Employee ID
                                    "SeNm": data['last_name'],      # Search name
                                    "FiNm": data['first_name'],     # First Name
                                    "LaNm": data['last_name'],      # Last Name
                                    "SpNm": False,                  # Birthname seperately
                                    "NmBi": data['last_name'],      # Birthname
                                    # Use of name [{"id":"0","description":"Birth name"},{"id":"1","description":"Partner's birth name + Birth name"},{"id":"2","description":"Partner birth name"},{"id":"3","description":"Birth name + Partner's birth name"}]
                                    "ViUs": "0",
                                    # Gender [{"id":"M","description":"Male"},{"id":"U","description":"Unknown"},{"id":"F","description":"Female"}]
                                    "ViGe": data['gender'],
                                    "PsNa": data['country'],        # Nationality
                                    "DaBi": data['date_of_birth'],  # Birth date
                                    "CoBi": data['country_of_birth'],  # Country of birth
                                    "RsBi": data['place_of_birth'],  # Place of birth
                                    "SoSe": data['ssn'],            # SSN
                                    "EmAd": data['email_work'],     # Company emailaddress
                                    "EmA2": data['email_home']      # Private emailaddress
                                },
                                "Objects": {
                                    "KnBasicAddressAdr": {
                                        "Element": {
                                            "Fields": {
                                                "CoId": data['country'],    # Country
                                                "PbAd": True,               # Postbusadres
                                                "Ad": data['street'],       # Street
                                                "HmNr": data['house_number'], # Streetnumber
                                                "ZpCd": data['postal_code'],  # Postal code
                                                "Rs": data['city'],         # City
                                                "ResZip": True              # Lookup city with postal code
                                            }
                                        }
                                    },
                                    "KnBasicAddressPad": {
                                        "Element": {
                                            "Fields": {
                                                "CoId": data['country'],     # Country
                                                "PbAd": True,                # Postbusadres
                                                "Ad": data['street'],        # Street
                                                "HmNr": data['house_number'],# Streetnumber
                                                "ZpCd": data['postal_code'], # Postal code
                                                "Rs": data['city'],          # City
                                                "ResZip": True               # Lookup city with postal code
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "AfasContract": {
                            "Element": {
                                "@DaBe": data['date_effective'],
                                "Fields": {
                                    "ClId": data['collective_agreement'],   # Cao - fixed
                                    "WcId": data['employment_conditions'],  # Arbeidsvoorwaarde - Fixed op zoetwarenindustrie - 36 uur
                                    "ApCo": data['type_of_contract'],       # Type of contract
                                    "CmId": data['employer'],                           # employer - fixed
                                    "EmMt": data['type_of_employee'],       # Type of employee (1=personeelslid)
                                    "ViEt": data['employment']              # Dienstbetrekking
                                }
                            }
                        },
                        "AfasOrgunitFunction": {
                            "Element": {
                                "@DaBe": data['date_effective'],            # Startdate organizational unit
                                "Fields": {
                                    "DpId": data['organizational_unit'],    # OE
                                    "FuId": data['function_id'],            # Function 0232=medewerk(st)er
                                    "CcId": data['costcarrier'],            # fixed on default: Profit
                                    "CrId": data['costcenter']              # Cost center
                                }
                            }
                        },
                        "AfasTimeTable": {
                            "Element": {
                                "@DaBg": data['date_effective'],            # Startdate Timetable
                                "Fields": {
                                    "StPa": True,                           # Wisselend arbeidspatroon
                                    "HrWk": data['weekly_hours'],           # Weekly hours
                                    "PcPt": data['parttime_percentage']     # Parttime percentage
                                }
                            }
                        },
                        "AfasSalary": {
                            "Element": {
                                "@DaBe": data['date_effective'],            # Startdate salary
                                "Fields": {
                                    "SaPe": ['type_of_salary'],             # Sort of salary - fixed (V=vast)
                                    "EmSa": data['amount'],                 # Salary amount
                                    "PtId": 5                               # Period table - fixed (periode HRM)
                                }
                            }
                        }
                    }
                }
            }
        }

    def post(self, rest_type, updateconnector, data):
        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, updateconnector)

        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        update = requests.request(rest_type, url, data=data, headers=headers)

        return update