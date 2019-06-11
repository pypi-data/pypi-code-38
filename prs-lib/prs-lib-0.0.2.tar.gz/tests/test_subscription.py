def test_get_subscription_json(client_with_auth):
    user_address = client_with_auth.config.address
    res = client_with_auth.subscription.get_subscription_json(user_address)
    assert res.status_code == 200
    assert res.content


def test_get_subscriptions(client_with_auth):
    user_address = client_with_auth.config.address
    res = client_with_auth.subscription.get_subscriptions(
        user_address, offset=0, limit=10
    )
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)


def test_get_subscribers(client_with_auth):
    user_address = client_with_auth.config.address
    res = client_with_auth.subscription.get_subscribers(
        user_address, offset=0, limit=10
    )
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)


def test_get_recommendation_json(client_with_auth):
    res = client_with_auth.subscription.get_recommendation_json(
        offset=0, limit=10
    )
    assert res.status_code == 200


def test_get_recommendations(client_with_auth):
    res = client_with_auth.subscription.get_recommendations(
        offset=0, limit=10
    )
    assert res.status_code == 200


def test_subscribe(client_with_auth, client_buyer):
    # subscribe
    buyer_address = client_buyer.config.address
    res = client_with_auth.subscription.subscribe(buyer_address)
    assert res.status_code == 200

    # check_subscription
    user_address = client_with_auth.config.address
    res = client_with_auth.subscription.check_subscription(
        user_address, buyer_address
    )
    assert res.status_code == 200

    # unsubscribe
    res = client_with_auth.subscription.unsubscribe(buyer_address)
    assert res.status_code == 200
