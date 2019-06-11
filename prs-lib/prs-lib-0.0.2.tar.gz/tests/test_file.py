def test_sign_file(client_with_auth, markdown_file):
    with open(markdown_file) as fp:
        data = {
            'stream': fp,
            'filename': markdown_file.basename,
            'title': f'{markdown_file} title',
        }
        res = client_with_auth.file.sign_by_stream(data)
        assert res.status_code == 200
        data = res.json()
        file_hash = data['cache']['msghash']
        assert file_hash
        file_rid = data['cache']['rId']
        assert file_rid


def test_file_methods(client_with_auth, client_buyer, markdown_file):
    # test sign with meta
    with open(markdown_file) as fp:
        data = {
            'stream': fp,
            'filename': markdown_file.basename,
            'title': f'{markdown_file} title',
        }
        meta = {'uuid': 'xxxxxx'}
        res = client_with_auth.file.sign_by_stream(data, meta)
        assert res.status_code == 200
        data = res.json()
        file_hash = data['cache']['msghash']
        assert file_hash
        file_rid = data['cache']['rId']
        assert file_rid

    # test get file by rid
    res = client_with_auth.file.get_by_rid(file_rid)
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)

    # test get file by msghash
    res = client_with_auth.file.get_by_msghash(file_hash)
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)

    # get feeds
    address = client_with_auth.config.address
    res = client_with_auth.file.get_feeds(
        address, offset=0, limit=10
    )
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)

    # test reward
    res = client_buyer.file.reward(file_rid, 1, 'hello')
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)
