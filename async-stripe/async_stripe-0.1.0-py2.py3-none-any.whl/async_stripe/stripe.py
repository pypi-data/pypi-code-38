"""Simple asynchronous `Stripe stripe`_ API payment wrapper

Authors: `cglacet cglacet`_

.. _stripe: https://stripe.com/docs/api/payment_intents/create#intro
.. _cglacet: https://github.com/cglacet
"""
import os
import asynctools
from aiohttp_params import session_complex_params
from contextlib import asynccontextmanager
import uuid

API_KEY_ENV_NAME = 'STRIPE_KEY'
API_KEY = os.getenv(API_KEY_ENV_NAME)
PUBLIC_KEY = "pk_test_6XtS5rPiYgsQvF6h872XpRjw00tTU6DCd0"
ROOT_URL = "https://api.stripe.com/v1"
PAYMENT_URL = f"{ROOT_URL}/payment_intents"
EVENTS_URL = f"{ROOT_URL}/events"


if API_KEY is None:
    raise EnvironmentError(
        "No API key set, please set your private API key"
        "in the envrionement variable, for example in bash: \n"
        f"   export {API_KEY_ENV_NAME}='sk_test_xxxxxxxxxxxxxxxxx'.\n\n"
        "Your key can be found at https://dashboard.stripe.com/account/apikeys.\n"
    )

class Stripe(asynctools.AbstractSessionContainer):
    def __init__(self, raise_for_status=False):
        super().__init__(raise_for_status=raise_for_status)

    async def session_hook(self, session):
        return session_complex_params(session)

    @asynccontextmanager
    @asynctools.attach_session
    async def post(self, url, params, session=None):
        async with session.post(url, params=params, headers=stripe_header()) as response:
            yield response

    @asynccontextmanager
    @asynctools.attach_session
    async def get(self, url, params, session=None):
        async with session.get(url, params=params, headers=stripe_header()) as response:
            yield response

    def create_payment(self, **params):
        return self.post(PAYMENT_URL, params)

    def update_payment(self, payment_intent, **params):
        return self.post(f"{PAYMENT_URL}/{payment_intent}", params)

    def events_list(self, session=None, **params):
        return self.get(EVENTS_URL, params)


# Example
class StripeImplementation:
    def create_payment(self, **params):
        params = {
            **params,
            "payment_method_types": ["card"],
        }
        return super().create_payment(**params)


def stripe_header():
    return {
        "Idempotency-Key": idempotency_key(),
        "Authorization": f"Bearer {API_KEY}",
    }


def idempotency_key():
    return str(uuid.uuid4())


if __name__ == "__main__":
    async def create_and_modify():
        async with Stripe() as stripe:
            params = dict(amount="1000", currency="eur", receipt_email="cglacet@kune.tech")
            async with stripe.create_payment(**params) as response:
                payment = await response.json()
                payment_intent = payment["id"]
                print("Created payment", payment["amount"], payment["currency"])

            params = dict(amount="500", currency="usd")
            async with stripe.update_payment(payment_intent, **params) as response:
                payment = await response.json()
                payment_intent = payment["id"]
                print("Updated payment", payment["amount"], payment["currency"])

    async def event_list():
        async with Stripe() as stripe:
            async with stripe.events_list(limit=10, type="*.succeeded") as response:
                json = await response.json()
                for event in json["data"]:
                    # print(event.keys())
                    # print(event["type"])
                    # print(event["data"]["object"].keys())
                    details = event["data"]["object"]
                    canceled_at = details.get("canceled_at", None)
                    print(details)
                    if canceled_at is not None:
                        continue

                    metadata = event["data"]["object"]["metadata"]
                    print("This is ok", metadata)


    import asyncio
    asyncio.run(create_and_modify())
    asyncio.run(event_list())