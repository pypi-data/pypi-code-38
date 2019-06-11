from .test_contract import create_contract, sign_markdown_file


def test_order(client_with_auth, client_buyer, markdown_file):
    # create order
    contract_rid = create_contract(client_with_auth)
    file_rid = sign_markdown_file(client_with_auth, markdown_file)
    res = client_with_auth.contract.bind(
        contract_rid, file_rid, client_with_auth.config.address
    )
    assert res.status_code == 200
    res = client_buyer.order.create(contract_rid, file_rid, 'usage1')
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)
    rid = data['rId']
    assert rid

    # FIXME: why can not use `rid` variable?
    valid_rid = '84f20b6885f02a2759d5414e360521fc410efa88c408fbcb2572cb9886baed50'
    res = client_buyer.order.get_order_by_rid(valid_rid)
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)
    assert 'order' in data
    assert 'contract' in data
    assert 'license' in data
    assert valid_rid == data['order']['rId']

    # get orders by contract_rid
    res = client_buyer.order.get_orders_by_contract_rid(contract_rid)
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)
    assert data['list'] and isinstance(data['list'], list)
    assert data['list'][0]['contract'] == contract_rid

    # get purchased orders
    res = client_buyer.order.get_purchased_orders(offset=0, limit=5)
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)
    assert data['list'] and isinstance(data['list'], list)
