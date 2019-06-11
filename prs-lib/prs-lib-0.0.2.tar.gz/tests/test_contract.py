def test_get_templates(client_with_auth):
    res = client_with_auth.contract.get_templates()
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)


def create_contract(c):
    code = (
        'PRSC Ver 0.1\n'
        'Name 购买授权\n'
        'Desc 这是一个\\n测试合约\n'
        f'Receiver {c.config.address}\n'
        'License usage1 CNB:0.001 Terms: 这是个人使用条款，禁止\\n商业应用。\n'
        'License usage2 CNB:0.002 Terms: 这是商业使用条款，允许\\n修改和复制。\n'
    )
    res = c.contract.create(code)
    data = res.json()
    assert data and isinstance(data, dict)
    contract_rid = data['contract']['rId']
    assert contract_rid
    return contract_rid


def test_create_and_get_contract(client_with_auth):
    contract_rid = create_contract(client_with_auth)
    assert contract_rid

    print('xxx contract_rid:', contract_rid)
    res = client_with_auth.contract.get_by_rid(contract_rid)
    assert res.status_code == 200
    print('xxx get_by_rid content:', res.content)
    data = res.json()
    assert data and isinstance(data, dict)

    resp = client_with_auth.contract.get_contracts(offset=0, limit=10)
    assert resp.status_code == 200
    print('xxx get_contracts content:', resp.content)
    data = resp.json()
    assert data and isinstance(data, dict)
    assert data['list'] and isinstance(data['list'], list)


def sign_markdown_file(c, f):
    with open(f) as fp:
        data = {'stream': fp, 'filename': 'xxx.md', 'title': 'xxx.md'}
        res = c.file.sign_by_stream(data)
        data = res.json()
        assert data and isinstance(data, dict)
        file_rid = data['cache']['rId']
        assert file_rid
        return file_rid


def test_sign_markdown_file(client_with_auth, markdown_file):
    assert sign_markdown_file(client_with_auth, markdown_file)


def test_bind_contract(client_with_auth, markdown_file):
    contract_rid = create_contract(client_with_auth)
    file_rid = sign_markdown_file(client_with_auth, markdown_file)
    resp = client_with_auth.contract.bind(
        contract_rid, file_rid, client_with_auth.config.address
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data and isinstance(data, dict)
