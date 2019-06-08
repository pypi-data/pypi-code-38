import requests
import json
from numbers import Number
from decimal import Decimal
from datetime import date


class ProxyPay():
	def __init__(self, api_key, is_production):
		self.api_key = api_key

		if is_production:
			self.endpoint = "https://api.proxypay.co.ao"
		else:
			self.endpoint = "https://api.sandbox.proxypay.co.ao"

		self.headers = headers = {'Accept': 'application/vnd.proxypay.v2+json', 'Authorization': 'Token {}'.format(self.api_key), 'Content-Type': 'application/json'}

	def _url(self, path):
		return self.endpoint + path

	def create_reference(self, reference_id, custom_fields=None, amount=None, expiry_date=None, product_ids=[]):
		#validate parameters
		self._validate_reference_id(reference_id)
		self._validate_custom_fields(custom_fields)
		self._validate_amount(amount)
		self._validate_expiry_date(expiry_date)
		self._validate_product_ids(product_ids)

		payload={}
		if not custom_fields == None:
			payload['custom_fields']=custom_fields
		if amount != None:
			payload['amount']=str(round(amount, 2))
		if expiry_date != None:
			payload['end_datetime']=expiry_date.isoformat()
		if product_ids != None:
			payload['product_ids']=product_ids

		try:
			r = requests.put(self._url('/references/{}'.format(reference_id)), headers=self.headers, data=json.dumps(payload))
			if r.status_code == 204:
				return {'success': True}
			if r.status_code == 400:
				return {'success': False, 'reason': r.json()}
			else:
				raise Exception('API returned status {}'.format(r.status_code))
		except:
			raise

	def delete_reference(self, reference_id):
		#Validate parameters
		self._validate_reference_id(reference_id)

		headers = {'Accept': 'application/vnd.proxypay.v2+json', 'Authorization': 'Token {}'.format(self.api_key)}
		try:
			r = requests.delete(self._url('/references/{}'.format(reference_id)), headers=self.headers)
			if r.status_code == 204:
				return {'success': True}
			else:
				raise Exception('API returned status {}'.format(r.status_code))
		except:
			raise

	def generate_reference_id(self):
		headers = {'Accept': 'application/vnd.proxypay.v2+json', 'Authorization': 'Token {}'.format(self.api_key)}
		try:
			r = requests.post(self._url('/reference_ids/'), headers=self.headers)
			if r.status_code == 200:
				return r.json()
			else:
				raise Exception('API returned status {}'.format(r.status_code))
		except:
			raise

	def get_payments(self):
		headers = {'Accept': 'application/vnd.proxypay.v2+json', 'Authorization': 'Token {}'.format(self.api_key)}
		try:
			r = requests.get(self._url('/payments/'), headers=self.headers)
			if r.status_code == 200:
				r.json()
				return {'success': True, 'data': r.json()}
			else:
				raise Exception('API returned status {}'.format(r.status_code))
		except:
			raise


	def acknowledge_payment(self, payment_id):
		#validate parameters
		self._validate_payment_id(payment_id)

		headers = {'Accept': 'application/vnd.proxypay.v2+json', 'Authorization': 'Token {}'.format(self.api_key)}
		try:
			r = requests.delete(self._url('/payments/{}'.format(payment_id)), headers=self.headers)
			if r.status_code == 204:
				return {'success': True}
			else:
				raise Exception('API returned status {}'.format(r.status_code))
		except:
			raise

	def _validate_reference_id(self, reference_id):
		if not isinstance(reference_id, Number):
			raise Exception('reference_id: "{}" not valid. Integer value expected.'.format(reference_id))

	def _validate_payment_id(self, payment_id):
		if not isinstance(payment_id, Number):
			raise Exception('payment_id: "{}" not valid. Integer value expected.'.format(payment_id))

	def _validate_custom_fields(self, custom_fields):
		if custom_fields != None and not isinstance(custom_fields, dict):
			raise Exception('custom_fields: "{}" not valid. Dict value expected'.format(custom_fields))

	def _validate_amount(self, amount):
		if amount != None and not isinstance(amount, Number):
			raise Exception('amount: "{}" not valid. Float value expected.'.format(amount))

	def _validate_expiry_date(self, expiry_date):
		if expiry_date != None and not isinstance(expiry_date, date):
			raise Exception('expiry_date: "{}" not valid. Date value expected.'.format(expiry_date))

	def _validate_product_ids(self, product_ids):
		if product_ids != None and not isinstance(product_ids, list):
			raise Exception('product_ids: "{}" not valid. List of integers value expected.'.format(product_ids))






