import datetime
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from invoices.models import Invoice, InvoiceLine
from register.dates import get_ranges_for_dates


INVOICE_PREFIX = settings.INVOICE_PREFIX
DEBCONF_NAME = settings.DEBCONF_NAME


FEE_INVOICE_INFO = {
    'pro': {
        'reference': INVOICE_PREFIX + 'REG-PRO',
        'description': '%s Professional registration fee' % DEBCONF_NAME,
        'unit_price': 200,
    },
    'corp': {
        'reference': INVOICE_PREFIX + 'REG-CORP',
        'description': '%s Corporate registration fee' % DEBCONF_NAME,
        'unit_price': 500,
    },
}

MEAL_PRICES = {
    'breakfast': None,
    'lunch': Decimal(5),
    'dinner': Decimal(5),
    'conference_dinner': Decimal(20),
}

ACCOMM_INVOICE_INFO = {
    'reference': INVOICE_PREFIX + 'ACCOMM',
    'description': '%s on-site accommodation' % DEBCONF_NAME,
    'unit_price': 5,
}


def invoice_user(user, force=False, save=False):
    from bursary.models import Bursary

    attendee = user.attendee

    try:
        bursary = user.bursary
    except Bursary.DoesNotExist:
        bursary = Bursary()

    lines = []
    fee_info = FEE_INVOICE_INFO.get(attendee.fee)
    if fee_info:
        fee_info['quantity'] = 1
        lines.append(InvoiceLine(**fee_info))

    try:
        accomm = attendee.accomm
    except ObjectDoesNotExist:
        accomm = None

    if accomm and not bursary.potential_bursary('accommodation'):
        for line in invoice_accomm(accomm):
            lines.append(InvoiceLine(**line))

    try:
        food = attendee.food
    except ObjectDoesNotExist:
        food = None

    if food and not bursary.potential_bursary('food'):
        for line in invoice_food(food):
            lines.append(InvoiceLine(**line))

    for paid_invoice in user.invoices.filter(status='paid', compound=False):
        lines.append(InvoiceLine(
            reference='INV#{}'.format(paid_invoice.reference_number),
            description='Previous Payment Received',
            unit_price=-paid_invoice.total,
            quantity=1,
        ))

    invoice = Invoice(
        recipient=user,
        status='new',
        date=timezone.now(),
        invoiced_entity=attendee.invoiced_entity,
        billing_address=attendee.billing_address
    )

    # Only save invoices if non empty
    if save and lines:
        invoice.save()

    total = 0
    for i, line in enumerate(lines):
        line.line_order = i
        total += line.total
        if save:
            line.invoice_id = invoice.id
            line.save()

    return {
        'invoice': invoice,
        'lines': lines,
        'total': total,
        'total_local': total * settings.DEBCONF_LOCAL_CURRENCY_RATE,
    }


def invoice_food(food):
    """Generate one invoice line per meal type per consecutive stay"""
    from register.models.food import Meal

    for meal, meal_label in Meal.MEALS.items():
        dates = [entry.date for entry in food.meals.filter(meal=meal)
                 if not entry.conference_dinner]
        if not dates:
            continue

        unit_price = MEAL_PRICES[meal]

        ranges = get_ranges_for_dates(dates)
        for first, last in ranges:
            n_meals = (last - first).days + 1

            if first != last:
                desc = "%s to %s" % (first, last)
            else:
                desc = str(first)

            full_desc = '%s %s (%s)' % (DEBCONF_NAME, meal_label, desc)
            yield {
                'reference': '%s%s' % (INVOICE_PREFIX, meal.upper()),
                'description': full_desc,
                'unit_price': unit_price,
                'quantity': n_meals,
            }

    if food.meals.filter(meal='dinner',
                         date=settings.DEBCONF_CONFERENCE_DINNER_DAY):
        yield {
            'reference': '%sCONFDINNER' % INVOICE_PREFIX,
            'description': '{} Conference Dinner ({})'.format(
                DEBCONF_NAME,
                settings.DEBCONF_CONFERENCE_DINNER_DAY.isoformat()),
            'unit_price': MEAL_PRICES['conference_dinner'],
            'quantity': 1,
        }


def invoice_accomm(accomm):
    """Generate one invoice line per consecutive stay"""
    stays = get_ranges_for_dates(
        night.date for night in accomm.nights.all()
    )

    for first_night, last_night in stays:
        last_morning = last_night + datetime.timedelta(days=1)
        num_nights = (last_morning - first_night).days
        desc = "evening of %s to morning of %s" % (first_night,
                                                   last_morning)

        line = ACCOMM_INVOICE_INFO.copy()
        line['description'] += ' ({})'.format(desc)
        line['quantity'] = num_nights
        yield line
