"""This is a server that allows to use the Payment intents from Stripe.

Quickstart guide from Stipe can be found here (this server is an implementation of this quickstart guide):
    https://stripe.com/docs/payments/payment-intents/quickstart


While in developement, you can run::
    uvicorn server:app --reload

Your app will be accessible at::

    http://127.0.0.1:8000/create_payment?amount=1000&currency=eur&receipt_email=cglacet@kune.tech

For production server, you may want to run something that look like::
    gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker

If you are inside a virtualenv, it's possible that gunicorn is not mapped correctly to the local version.
In which case you will probably see an error message saying::

    Error: class uri 'uvicorn.workers.UvicornWorker' invalid or not found:

If that's the case, then don't forget to activate the virtual env before running the app:

    . .venv/bin/actiate

Accessible at:
    http://0.0.0.0:5000/create_payment?amount=1000&currency=eur&receipt_email=cglacet@kune.tech


Author: `cglacet cglacet`_

.. _cglacet: https://github.com/cglacet
"""
from babel import numbers, Locale

from fastapi import FastAPI
from pydantic import BaseModel

from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from async_stripe import Stripe

DEFAULT_LOCALE = "fr_FR"

## Load this from a environement variable ? $ALLOWED_HOSTS
ALLOWED_HOSTS = None
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stripe = Stripe()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    await stripe.start_session()
    print("Stripe session opened.")

@app.on_event("shutdown")
async def shutdown_event():
    await stripe.close_session()
    print("Stripe session closed.")

@app.get('/')
async def hello():
    return "This is the Stripe API ASGI server!"


class Item(BaseModel):
    amount: str
    currency: str
    receipt_email: str


@app.post('/create_payment')
async def create_payment(body: Item):
    """Creates a payment intent, the stripe response.
    The response details can be found on the stripe API documentation:
    `PaymentIntent object <https://stripe.com/docs/api/payment_intents/object>`.

    Call example::
        http://127.0.0.1:8000/create_payment

    With body set to::
        { "amount": 1000, "currency": "eur", "receipt_email": "cglacet@kune.tech" }

    """
    params = {
        "amount": body.amount,
        "currency": body.currency,
        "receipt_email": body.receipt_email,
    }
    return await payment(**params)


@app.get('/create_payment_form')
async def create_payment_form(request: Request, amount: int, currency: str, receipt_email: str):
    """Creates a payment and directly returns the HTML payment form.

    Call example::
        http://127.0.0.1:8000/create_payment_form?amount=1000&currency=eur&receipt_email=cglacet@kune.tech

    """
    intent = await payment(amount=amount, currency=currency, receipt_email=receipt_email)
    return payment_form(request, intent)


@app.get('/get_payment_form/{payment_id}')
async def get_payment_form(request: Request, payment_id: str, amount: int = None, currency: str = None, receipt_email: str = None):
    """Returns the payment form associated to the given payment ``payment_id``.
    This returns the HTML payment form.

    This will update the payment if any optional parameter is provided.

    The ``payment_id`` is of the form ``pi_xxxxxxxxxxxxxxxxxxxxxxxx``.

    Call example::
        http://127.0.0.1:8000/get_payment_form/pi_1EjZm4ColNztjCkCmEFngFgB

    """
    # Maybe require currency when amount is requested for a change?
    update_payment = stripe.update_payment(payment_id, amount=amount, currency=currency, receipt_email=receipt_email)
    async with update_payment as response:
        intent = await response.json()
        return payment_form(request, intent)

async def payment(**params):
    options = {
        "description": "Test payement",
        "statement_descriptor": "Kune.tech",
    }
    async with stripe.create_payment(**params, **options) as response:
        return await response.json()


def payment_form(request: Request, intent):
    """Returns the HTML payment form with the specified parameters

    The ``payment_id`` is of the form ``pi_xxxxxxxxxxxxxxxxxxxxxxxx``.

    Call example::
        http://127.0.0.1:8000/payment_form/pi_1EjZm4ColNztjCkCmEFngFgB?amount=1000&currency=eur

    """
    template_params = {
        "request": request,
        "localized_price_tag": localized_price_tag(intent),
        **intent
    }
    return templates.TemplateResponse("checkout.html", template_params)


def localized_price_tag(payment_intent, locale=DEFAULT_LOCALE, **kwargs):
    """Format price according to an optional ``locale``.
    For example::

        >>> format_price(1000, "EUR")
        10 €
        >>> format_price(1050, "EUR")
        10,50 €
        >>> format_price(1050, "EUR", locale="en_US")
        €10.50
    """
    amount = payment_intent["amount"]/100
    # http://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_currency:
    # return numbers.format_currency(amount, currency.upper(), locale=locale, decimal_quantization=False, **kwargs)
    # https://github.com/python-babel/babel/issues/478#issuecomment-290365787:
    return _custom_format_currency(amount, payment_intent["currency"].upper(), locale)



def _custom_format_currency(value, currency, locale):
    value = numbers.decimal.Decimal(value)
    locale = Locale.parse(locale)
    pattern = locale.currency_formats['standard']
    force_frac = ((0, 0) if value == int(value) else None)
    return pattern.apply(value, locale, currency=currency, force_frac=force_frac)


if __name__ == "__main__":
    import uvicorn
    import os
    script_py_name = os.path.basename(__file__)
    script_name = os.path.splitext(script_py_name)[0]
    uvicorn.run(f"{script_name}:app", reload=True, debug=True, log_level="info")