from simple.client_context import ClientContext
from simple.signature import Signature
from openapi_client.api.authentication_api import AuthenticationApi
from openapi_client.api.order_api import OrderApi
from openapi_client.api.payment_api import PaymentApi
from openapi_client.api.card_verification_api import CardVerificationApi
from openapi_client.api.currency_conversion_api import CurrencyConversionApi
from openapi_client.api.fraud_detect_api import FraudDetectApi
from openapi_client.api.payment_schedules_api import PaymentSchedulesApi
from openapi_client.api.payment_token_api import PaymentTokenApi
from openapi_client.api.payment_url_api import PaymentURLApi
from openapi_client.api.card_info_lookup_api import CardInfoLookupApi

class Gateway:
	
	CONTENT_TYPE = 'application/json'

	@staticmethod
	def create(creds):
		return Gateway(ClientContext(creds))

	def __init__(self, context):
		self.context = context
		self.authentication_api = AuthenticationApi()
	 	self.order_api = OrderApi()
		self.payment_api = PaymentApi()
		self.card_verification_api = CardVerificationApi()
		self.currency_conversion_api = CurrencyConversionApi()
		self.fraud_detect_api = FraudDetectApi()
		self.payment_schedules_api = PaymentSchedulesApi()
		self.payment_token_api = PaymentTokenApi()
		self.payment_url_api = PaymentURLApi()
		self.card_info_lookup_api = CardInfoLookupApi()

	# Authentication API
	def request_access_token(self):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign()
		return self.authentication_api.authentication_access_tokens_post(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			message_signature=message_signature
		)

	# Payment API
	def finalize_secure_transaction(self, transaction_id, payload, region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign(payload)
		return self.payment_api.finalize_secure_transaction(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			transaction_id,
			payload,
			message_signature=message_signature,
			region=region
		)

	def primary_payment_transaction(self, payload, region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign(payload)
		return self.payment_api.submit_primary_transaction(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			payload,
			message_signature=message_signature,
			region=region
		)

	def secondary_payment_transaction(self, transaction_id, payload, store_id='', region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign(payload)
		return self.payment_api.submit_secondary_transaction(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			transaction_id,
			payload,
			message_signature=message_signature,
			store_id=store_id,
			region=region
		)

	def transaction_inquiry(self, transaction_id, store_id='', region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign()
		return self.payment_api.transaction_inquiry(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			transaction_id,
			message_signature=message_signature,
			store_id=store_id,
			region=region
		)

	# Order API
	def order_inquiry(self, order_id, store_id='', region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign()
		return self.order_api.order_inquiry(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			order_id,
			message_signature=message_signature,
			store_id=store_id,
			region=region
		)

	def perform_secondary_transaction_by_order(self, order_id, payload, region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign(payload)
		return self.order_api.submit_secondary_transaction_from_order(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			order_id,
			payload,
			message_signature=message_signature,
			region=region
		)

	# Card Verification API
	def verify_card(self, payload, region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign(payload)
		return self.card_verification_api.verify_card(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			payload,
			message_signature=message_signature,
			region=region
		)

	# Currency Conversion API
	def get_exchange_rate(self, payload, region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign(payload)
		return self.currency_conversion_api.get_exchange_rate(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			payload,
			message_signature=message_signature,
			region=region
		)

	# Fraud Detect API
	def get_transaction_fraud_score(self, payload, region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign(payload)
		return self.fraud_detect_api.score_only(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			payload,
			message_signature=message_signature,
			region=region
		)	

	# Payment Schedules API
	def create_payment_schedule(self, payload, region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign(payload)
		return self.payment_schedules_api.create_payment_schedule(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			payload,
			message_signature=message_signature,
			region=region
		)

	def update_payment_schedule(self, order_id, payload, store_id='', region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign(payload)
		return self.payment_schedules_api.update_payment_schedule(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			order_id,
			payload,
			message_signature=message_signature,
			store_id=store_id,
			region=region
		)

	def cancel_payment_schedule(self, order_id, store_id='', region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign()
		return self.payment_schedules_api.cancel_payment_schedule(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			order_id,
			message_signature=message_signature,
			store_id=store_id,
			region=region
		)

	def payment_schedule_inquiry(self, order_id, store_id='', region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign()
		return self.payment_schedules_api.inquiry_payment_schedule(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			order_id,
			message_signature=message_signature,
			store_id=store_id,
			region=region
		)

	# Payment Token API
	def create_payment_token(self, payload, authorization='', region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign(payload)
		return self.payment_token_api.create_payment_token(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			payload,
			message_signature=message_signature,
			authorization=authorization,
			region=region
		)

	def delete_payment_token(self, token_id, authorization='', store_id='', region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign()
		return self.payment_token_api.delete_payment_token(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			token_id,
			message_signature=message_signature,
			authorization=authorization,
			store_id=store_id,
			region=region
		)

	# Payment URL API
	def create_payment_url(self, payload, region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign(payload)
		return self.payment_url_api.create_payment_url(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			payload,
			message_signature=message_signature,
			region=region
		)

	# Card Info Lookup API
	def card_info_lookup(self, payload, region=''):
		signature_service = self.get_signature_service()
		message_signature = signature_service.sign(payload)
		return self.card_info_lookup_api.card_info_lookup(
			self.CONTENT_TYPE,
			signature_service.client_request_id,
			self.get_api_key(),
			signature_service.timestamp,
			payload,
			message_signature=message_signature,
			region=region
		)

	def get_signature_service(self):
		return Signature({
			"api_key":self.get_api_key(),
			"api_secret":self.get_api_secret()
		})

	def get_api_key(self):
		return self.context.credentials.get_api_key()

	def get_api_secret(self):
		return self.context.credentials.get_api_secret()