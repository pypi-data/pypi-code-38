__author__ = "UShareSoft"


def validate(quota):
    if quota.frequency is not None:
        if quota.frequency != "monthly" and quota.frequency != "none":
            raise ValueError("The frequency is not defined or correct.")
    if quota.limit is not None and quota.unlimited:
        raise ValueError("You can't set a defined limit and on the other hand set an unlimited limit.")


def update(existing_quota, new_quota):
    existing_quota.type = new_quota.type
    if new_quota.frequency is not None:
        existing_quota.frequency = new_quota.frequency
    if new_quota.unlimited:
        existing_quota.limit = -1
    else:
        existing_quota.limit = new_quota.limit
