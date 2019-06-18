import pytest

from fares import (
    is_subscription_offering_applicable_for_usage,
    SubscriptionOffering,
    is_subscription_offering_applicable_for_purchase,
)
from fares.dimension import UserDimensions, SlotDimensions


@pytest.fixture
def subscription_offering_single_od_session():
    return {
        "id": "first_sub",
        "name": "Morning sub",
        "rides": "10",
        "currency": "INR",
        "validity_in_days": "20",
        "is_carry_forward": "True",
        "activation_date": "2019-02-28T12:56:41.589953+00:00",
        "deactivation_date": "2019-02-28T12:56:41.589953+00:00",
        "zone_id": "zone1",
        "amount": "1000",
        "subscription_type": "STANDARD",
        "applicability": {
            "type": "INTER_CLUSTER",
            "rules": [
                {
                    "origin_cluster_id": "cluster_1",
                    "destination_cluster_id": "cluster_2",
                    "session": "MORNING",
                }
            ],
        },
        "created_at": "2019-02-28T12:56:41.589953+00:00",
    }


@pytest.fixture
def subscription_offering_multiple_od_session():
    return {
        "id": "first_sub",
        "name": "Morning sub",
        "rides": "10",
        "currency": "INR",
        "validity_in_days": "20",
        "is_carry_forward": "True",
        "activation_date": "2019-02-28T12:56:41.589953+00:00",
        "deactivation_date": "2019-02-28T12:56:41.589953+00:00",
        "zone_id": "zone1",
        "amount": "1000",
        "subscription_type": "TRIAL",
        "applicability": {
            "type": "INTER_CLUSTER",
            "rules": [
                {
                    "origin_cluster_id": "cluster_2",
                    "destination_cluster_id": "cluster_1",
                    "session": "MORNING",
                },
                {
                    "origin_cluster_id": "cluster_2",
                    "destination_cluster_id": "cluster_1",
                    "session": "EVENING",
                },
            ],
        },
        "created_at": "2019-02-28T12:56:41.589953+00:00",
    }


@pytest.fixture
def subscription_offering_multiple_ods():
    return {
        "id": "first_sub",
        "name": "Morning sub",
        "rides": "10",
        "currency": "INR",
        "validity_in_days": "20",
        "is_carry_forward": "True",
        "activation_date": "2019-02-28T12:56:41.589953+00:00",
        "deactivation_date": "2019-02-28T12:56:41.589953+00:00",
        "zone_id": "zone1",
        "amount": "1000",
        "subscription_type": "TRIAL",
        "applicability": {
            "type": "INTER_CLUSTER",
            "rules": [
                {
                    "origin_cluster_id": "cluster_2",
                    "destination_cluster_id": "cluster_1",
                    "session": "MORNING",
                },
                {
                    "origin_cluster_id": "cluster_2",
                    "destination_cluster_id": "cluster_1",
                    "session": "EVENING",
                },
                {
                    "origin_cluster_id": "cluster_3",
                    "destination_cluster_id": "cluster_4",
                    "session": "MORNING",
                },
                {
                    "origin_cluster_id": "cluster_3",
                    "destination_cluster_id": "cluster_4",
                    "session": "EVENING",
                },
            ],
        },
        "created_at": "2019-02-28T12:56:41.589953+00:00",
    }


@pytest.fixture
def subscription_offering_with_morning_session():
    return {
        "id": "first_sub",
        "name": "Morning sub",
        "rides": "10",
        "currency": "INR",
        "validity_in_days": "20",
        "is_carry_forward": "True",
        "activation_date": "2019-02-28T12:56:41.589953+00:00",
        "deactivation_date": "2019-02-28T12:56:41.589953+00:00",
        "zone_id": "zone1",
        "amount": "1000",
        "subscription_type": "TRIAL",
        "applicability": {
            "type": "INTER_CLUSTER",
            "rules": [
                {
                    "origin_cluster_id": "cluster_2",
                    "destination_cluster_id": "cluster_1",
                    "session": "MORNING",
                }
            ],
        },
        "created_at": "2019-02-28T12:56:41.589953+00:00",
    }


@pytest.fixture
def subscription_offering_zone_applicability():
    return {
        "id": "first_sub",
        "name": "Morning sub",
        "rides": "10",
        "currency": "INR",
        "validity_in_days": "20",
        "is_carry_forward": "True",
        "activation_date": "2019-02-28T12:56:41.589953+00:00",
        "deactivation_date": "2019-02-28T12:56:41.589953+00:00",
        "zone_id": "zone-1",
        "amount": "1000",
        "subscription_type": "TRIAL",
        "applicability": {"type": "ZONE_WIDE", "rules": [{"zone_id": "zone-1"}]},
        "created_at": "2019-02-28T12:56:41.589953+00:00",
    }


@pytest.fixture
def morning_slot():
    return {
        SlotDimensions.ORIGIN_CLUSTER_ID: "cluster_1",
        SlotDimensions.DESTINATION_CLUSTER_ID: "cluster_2",
        SlotDimensions.SESSION: "MORNING",
        SlotDimensions.ROUTE_ID: "route_id_1",
        SlotDimensions.START_TIME: "2019-02-28T4:56:41.589953+00:00",
    }


@pytest.fixture
def evening_slot():
    return {
        SlotDimensions.ORIGIN_CLUSTER_ID: "cluster_2",
        SlotDimensions.DESTINATION_CLUSTER_ID: "cluster_1",
        SlotDimensions.SESSION: "EVENING",
        SlotDimensions.ROUTE_ID: "route_id_1",
        SlotDimensions.START_TIME: "2019-02-28T12:56:41.589953+00:00",
    }


@pytest.fixture
def slot_with_wrong_od():
    return {
        SlotDimensions.ORIGIN_CLUSTER_ID: "cluster_2",
        SlotDimensions.DESTINATION_CLUSTER_ID: "cluster_4",
        SlotDimensions.SESSION: "EVENING",
        SlotDimensions.ROUTE_ID: "route_id_1",
        SlotDimensions.START_TIME: "2019-02-28T12:56:41.589953+00:00",
    }


@pytest.fixture
def zone_slot():
    return {
        SlotDimensions.ROUTE_ID: "route_id_1",
        SlotDimensions.START_TIME: "2019-02-28T12:56:41.589953+00:00",
        SlotDimensions.ZONE_ID: "zone-1",
    }


@pytest.fixture
def user_with_no_pass():
    return {UserDimensions.PASS_PURCHASE_COUNT: 0, UserDimensions.ID: "dummy_id"}


@pytest.fixture
def user_with_pass():
    return {UserDimensions.PASS_PURCHASE_COUNT: 1, UserDimensions.ID: "dummy_id_2"}


def test_is_offering_applicable_happy_single_od(
    subscription_offering_single_od_session, morning_slot
):
    assert is_subscription_offering_applicable_for_usage(
        SubscriptionOffering.from_json(subscription_offering_single_od_session),
        morning_slot,
    )


def test_is_offering_applicable_sad_single_od_inverse_slot(
    subscription_offering_single_od_session, morning_slot
):
    morning_slot[SlotDimensions.SESSION] = "EVENING"
    assert is_subscription_offering_applicable_for_usage(
        SubscriptionOffering.from_json(subscription_offering_single_od_session),
        morning_slot,
    )


def test_is_offering_applicable_happy_multiple_od(
    subscription_offering_multiple_od_session, evening_slot
):
    assert is_subscription_offering_applicable_for_usage(
        SubscriptionOffering.from_json(subscription_offering_multiple_od_session),
        evening_slot,
    )


def test_is_offering_applicable_sad_multiple_od(
    subscription_offering_multiple_od_session, morning_slot
):
    assert not is_subscription_offering_applicable_for_usage(
        SubscriptionOffering.from_json(subscription_offering_multiple_od_session),
        morning_slot,
    )


def test_is_offering_applicable_multiple_ods(
    subscription_offering_multiple_ods, evening_slot
):
    assert is_subscription_offering_applicable_for_usage(
        SubscriptionOffering.from_json(subscription_offering_multiple_ods), evening_slot
    )


def test_not_applicable_for_wrong_od(
    subscription_offering_multiple_ods, slot_with_wrong_od
):
    assert not is_subscription_offering_applicable_for_usage(
        SubscriptionOffering.from_json(subscription_offering_multiple_ods),
        slot_with_wrong_od,
    )


def test_session_does_not_matter(
    subscription_offering_with_morning_session, evening_slot
):
    assert is_subscription_offering_applicable_for_usage(
        SubscriptionOffering.from_json(subscription_offering_with_morning_session),
        evening_slot,
    )


def test_is_offering_applicable_for_purchase_trial_pass(
    subscription_offering_multiple_od_session, user_with_no_pass, user_with_pass
):
    assert is_subscription_offering_applicable_for_purchase(
        SubscriptionOffering.from_json(subscription_offering_multiple_od_session),
        user_with_no_pass,
    )

    assert not is_subscription_offering_applicable_for_purchase(
        SubscriptionOffering.from_json(subscription_offering_multiple_od_session),
        user_with_pass,
    )


def test_is_offering_applicable_for_purchase_standard_pass(
    subscription_offering_single_od_session, user_with_no_pass, user_with_pass
):
    assert is_subscription_offering_applicable_for_purchase(
        SubscriptionOffering.from_json(subscription_offering_single_od_session),
        user_with_no_pass,
    )

    assert is_subscription_offering_applicable_for_purchase(
        SubscriptionOffering.from_json(subscription_offering_single_od_session),
        user_with_pass,
    )


def test_is_offering_applicable_for_purchase_when_user_is_blacklisted(
    subscription_offering_zone_applicability
):
    blacklisted_user = {
        UserDimensions.PASS_PURCHASE_COUNT: 0,
        UserDimensions.ID: "di1",
        UserDimensions.BLACKLISTED: True,
    }
    assert not is_subscription_offering_applicable_for_purchase(
        SubscriptionOffering.from_json(subscription_offering_zone_applicability),
        blacklisted_user,
    )


def test_is_offering_applicable_for_purchase_when_user_is_blacklisted_with_standard_pass(
    subscription_offering_single_od_session
):
    blacklisted_user = {
        UserDimensions.PASS_PURCHASE_COUNT: 0,
        UserDimensions.ID: "di1",
        UserDimensions.BLACKLISTED: True,
    }
    assert is_subscription_offering_applicable_for_purchase(
        SubscriptionOffering.from_json(subscription_offering_single_od_session),
        blacklisted_user,
    )


def test_is_offering_applicable_for_purchase_when_user_is_not_blacklisted(
    subscription_offering_zone_applicability
):
    blacklisted_user = {UserDimensions.PASS_PURCHASE_COUNT: 0, UserDimensions.ID: "di1"}
    assert is_subscription_offering_applicable_for_purchase(
        SubscriptionOffering.from_json(subscription_offering_zone_applicability),
        blacklisted_user,
    )


def test_is_offering_applicable_with_zone_applicability(
    subscription_offering_zone_applicability, zone_slot
):
    assert is_subscription_offering_applicable_for_usage(
        SubscriptionOffering.from_json(subscription_offering_zone_applicability),
        zone_slot,
    )
