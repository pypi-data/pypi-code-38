from typing import Dict

from fares.dimension import (
    resolve_user_dimensions,
    zone_resolver,
    inter_cluster_resolver,
)
from fares.subscription_offering import SubscriptionOffering


def _get_usage_resolver(subscription_offering):
    if subscription_offering.applicability_type == "ZONE_WIDE":
        return zone_resolver
    elif subscription_offering.applicability_type == "INTER_CLUSTER":
        return inter_cluster_resolver
    else:
        raise TypeError("Invalid Applicability Type")


def is_subscription_offering_applicable_for_usage(
    subscription_offering: SubscriptionOffering, slot: Dict
):
    rule_set = subscription_offering.usage_applicability_rules()
    resolver = _get_usage_resolver(subscription_offering)
    return rule_set.evaluate(resolver(slot))


def is_subscription_offering_applicable_for_purchase(
    subscription_offering: SubscriptionOffering, user: Dict
):
    rule_set = subscription_offering.purchase_applicability_rules()
    context = resolve_user_dimensions(user)
    return rule_set.evaluate(context)
