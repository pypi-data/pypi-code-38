__author__ = 'SHASHANK'
from .constants import allotment_tat, redemption_tat
from datetime import timedelta


def flow_0_(t_date, partner_credit_date, calender, scheme_id):
    return t_date, None


def flow_0_bank(t_date, partner_credit_date, calender, scheme_id):
    return t_date, None


def flow_1_(t_date, partner_credit_date, calender, scheme_id):
    order_date = partner_credit_date
    while calender.is_scheme_holiday(order_date, scheme_id):
        order_date = calender.get_next_date(order_date)

    allotment_date = calender.get_next_date(order_date, sum(allotment_tat.get(scheme_id, [0, 1])))
    while calender.is_scheme_holiday(allotment_date, scheme_id):
        allotment_date = calender.get_next_date(allotment_date)
    return allotment_date, None


def flow_1_bank(t_date, partner_credit_date, calender, scheme_id):
    if t_date.hour >= 15:
        order_date = calender.get_next_date(t_date)
    else:
        order_date = calender.get_next_date(t_date, 0)
    while calender.is_scheme_holiday(order_date, scheme_id):
        order_date = calender.get_next_date(order_date)

    redemption_days = sum(map(lambda x: x[0] if scheme_id in x[1] else 0, redemption_tat.items()))
    redemption_date = calender.get_next_date(order_date, redemption_days if redemption_days != 0 else 3)
    while calender.is_scheme_holiday(redemption_date, scheme_id):
        redemption_date = calender.get_next_date(redemption_date)
    return redemption_date, None


def flow_2_(t_date, partner_credit_date, calender, scheme_id):
    return calender.get_next_date(partner_credit_date), None


def flow_2_bank(t_date, partner_credit_date, calender, scheme_id):
    return calender.get_next_date(partner_credit_date), None


def flow_3_(t_date, partner_credit_date, calender, scheme_id):
    return t_date, None


def flow_3_bank(t_date, partner_credit_date, calender, scheme_id):
    return t_date, None


def flow_4_(t_date, partner_credit_date, calender, scheme_id):
    return calender.get_next_date(t_date, 2), None


def flow_4_bank(t_date, partner_credit_date, calender, scheme_id):
    if t_date.hour >= 15:
        order_date = calender.get_next_date(t_date)
    else:
        order_date = calender.get_next_date(t_date, 0)
    return calender.get_next_date(order_date, 3), None


def flow_5_(t_date, partner_credit_date, calender, scheme_id):
    return t_date, None


def flow_5_bank(t_date, partner_credit_date, calender, scheme_id):
    return t_date, None


def flow_6_(t_date, partner_credit_date, calender, scheme_id):
    # t + timedelta(days=5) because of change in api response from faircent
    return calender.get_next_date(t_date, 2) + timedelta(days=5), None


def flow_6_bank(t_date, partner_credit_date, calender, scheme_id):
    if t_date.hour >= 15:
        order_date = calender.get_next_date(t_date)
    else:
        order_date = calender.get_next_date(t_date, 0)
    return calender.get_next_date(order_date, 3), None


def flow_7_(t_date, partner_credit_date, calender, scheme_id):
    return t_date, None


def flow_7_bank(t_date, partner_credit_date, calender, scheme_id):
    return t_date, None


def flow_8_(t_date, partner_credit_date, calender, scheme_id):
    return calender.get_next_date(t_date, 2), None


def flow_8_bank(t_date, partner_credit_date, calender, scheme_id):
    if t_date.hour >= 15:
        order_date = calender.get_next_date(t_date)
    else:
        order_date = calender.get_next_date(t_date, 0)
    return calender.get_next_date(order_date, 3), None


def flow_9_(t_date, partner_credit_date, calender, scheme_id):
    return calender.get_next_date(t_date, 2), None


def flow_9_bank(t_date, partner_credit_date, calender, scheme_id):
    if t_date.hour >= 15:
        order_date = calender.get_next_date(t_date)
    else:
        order_date = calender.get_next_date(t_date, 0)
    return calender.get_next_date(order_date, 3), None


def flow_10_(t_date, partner_credit_date, calender, scheme_id):
    return t_date, None


def flow_10_bank(t_date, partner_credit_date, calender, scheme_id):
    return t_date, None


def flow_11_(t_date, partner_credit_date, calender, scheme_id):
    return calender.get_next_date(t_date, 6), None


def flow_11_bank(t_date, partner_credit_date, calender, scheme_id):
    return calender.get_next_date(t_date, 4), None