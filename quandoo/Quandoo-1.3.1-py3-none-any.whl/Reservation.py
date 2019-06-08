import json

import requests

from quandoo.Error import PoorResponse
from quandoo.QuandooModel import urljoin, QuandooModel, QuandooDatetime


class Reservation(QuandooModel):

    def __init__(self, data, agent):
        print(json.dumps(data, indent=2))
        self.id = data["id"]
        self.status = data["status"]
        self.date = QuandooDatetime.parse_str_qdt(data["startTime"])
        self.startTime = QuandooDatetime.parse_str_qdt(data["startTime"])
        self.endTime = QuandooDatetime.parse_str_qdt(data["endTime"])
        self.capacity = data["capacity"]
        self.merchantId = data["merchantId"]
        self.customerId = data["customerId"]

        self.agent = agent

        super().__init__(data)

    def __str__(self):
        useful_attrs = []
        for key, val in self.__dict__.items():
            if key not in self.useless_attrs:
                if type(val) == QuandooDatetime:
                    if key == "date":
                        val = val.pretty_date().split(", ")[-1]
                    else:
                        val = val.pretty_date().split(", ")[0]
                useful_attrs.append("{}: {}".format(key, val))

        return "{}(\n\t{}\n)".format(
            self.__class__.__name__,
            ",\n\t".join(useful_attrs)
        )

    def cancel(self):
        data = {
            "reservation": {
                "status": "CUSTOMER_CANCELED"
            }
        }

        request = urljoin(self.agent.url, "reservations", self.id)
        response = requests.patch(request, headers=self.agent.headers, json=data)

        if response.status_code == 200:
            self.status = "CUSTOMER_CANCELED"
            return

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def reconfirm(self):
        data = {
            "reservation": {
                "status": "RECONFIRMED"
            }
        }

        request = urljoin(self.agent.url, "reservations", self.id)
        response = requests.patch(request, headers=self.agent.headers, json=data)

        if response.status_code == 200:
            self.status = "RECONFIRMED"
            return

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def change_capacity(self, new_capacity):
        data = {
            "reservation": {
                "capacity": new_capacity,
            }
        }

        request = urljoin(self.agent.url, "reservations", self.id)
        response = requests.patch(request, headers=self.agent.headers, json=data)

        if response.status_code == 200:
            self.capacity = new_capacity
            return

        raise PoorResponse(response.status_code, json.loads(response.text), request)


class NewReservation(QuandooModel):

    def __init__(self, data, agent):
        self.id = data["reservation"]["id"]
        self.number = data["reservation"]["number"]
        self.status = data["reservation"]["status"]
        self.customerId = data["customer"]["id"]

        self.agent = agent

        super().__init__(data)

    def get_reservation(self):
        return self.agent.get_reservation(self.id)

