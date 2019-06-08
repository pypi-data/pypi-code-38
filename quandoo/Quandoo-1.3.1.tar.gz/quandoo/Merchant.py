import json
from datetime import timedelta

import requests

from quandoo.Customer import Customer
from quandoo.Error import PoorResponse
from quandoo.QuandooModel import QuandooModel, QuandooDatetime, urljoin
from quandoo.Reservation import Reservation, NewReservation


class Merchant(QuandooModel):

    def __init__(self, data, agent):
        self.id = data["id"]
        self.name = data["name"]
        address_vals = [i if i in data["location"]["address"].keys() else "" for i in ['number', 'street', 'city', 'country']]
        address_vals[1] = " ".join(address_vals[:1])
        address_vals = address_vals[1:]
        self.address = ", ".join(address_vals)

        self.agent = agent

        super().__init__(data)

    def get_customers(self):
        request = urljoin(self.agent.url, "merchants", self.id, "customers")
        response = requests.get(request, headers=self.agent.headers)

        if response.status_code == 200:
            return [Customer(i, self.agent) for i in json.loads(response.text)["result"]]

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def get_reservations(self, limit=None, earliest=None, latest=None):
        params = {}
        if limit:
            params["limit"] = limit
        if earliest:
            params["earliest"] = earliest.get_urldt()
        if latest:
            params["latest"] = latest.get_urldt()

        request = "{}/merchants/{}/reservations".format(self.agent.url, self.id)
        response = requests.get(request, headers=self.agent.headers, params=params)

        if response.status_code == 200:
            return [Reservation(i, self.agent) for i in json.loads(response.text)["reservations"]]

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def get_available_times(self, pax: int, qdt: QuandooDatetime, duration=2, area_id=None):
        params = {
            "agentId": self.agent.agent_id,
            "capacity": pax,
            "fromTime": qdt.datetime.strftime("%H:%M"),
            "toTime": (qdt.datetime + timedelta(hours=duration)).strftime("%H:%M")
        }
        if area_id is not None:
            params["areaId"] = area_id

        request = urljoin(self.agent.url, "merchants", self.id, "availabilities", qdt.datetime.strftime("%Y-%m-%d"))
        response = requests.get(request, headers=self.agent.headers, params=params)

        if response.status_code == 200:
            return [QuandooDatetime.parse_str_qdt(i["dateTime"]) for i in json.loads(response.text)["timeSlots"]]

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def is_available(self, pax: int, qdt: QuandooDatetime):
        return qdt in self.get_available_times(pax, qdt)

    def create_reservation(self, customer, pax: int, qdt: QuandooDatetime, area_id=None, order_id=None, extra_info=None):
        data = {
            "reservation": {
                "merchantId": self.id,
                "capacity": pax,
                "dateTime": qdt.get_qdt()
            },
            "customer": customer.to_json(),
            "tracking": {
                "agent": {
                    "id": self.agent.agent_id
                }
            }
        }
        if area_id:
            data["reservation"]["areaId"] = area_id
        if order_id:
            data["reservation"]["orderId"] = order_id
        if extra_info:
            data["reservation"]["extraInfo"] = extra_info

        request = urljoin(self.agent.url, "reservations")
        response = requests.put(request, headers=self.agent.headers, json=data)

        if response.status_code == 200:
            return NewReservation(json.loads(response.text), self.agent)

        raise PoorResponse(response.status_code, json.loads(response.text), request)

