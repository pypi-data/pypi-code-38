from prs_lib import PRS


DETAIL_PROPERTIES = ['userName', 'userAvatar', 'userTitle', 'title', 'url']
VALID_BLOCKS = [
    'cfe123d4e2bc4d7c8819b948151eb024eaaff81d7273bc273ebba0e5736b80d9',
]


def test_get_blocks_by_rids_without_detail(client_without_auth):
    res = client_without_auth.block.get_by_rids(VALID_BLOCKS)
    assert res.status_code == 200
    lst = res.json()
    assert isinstance(lst, list)
    for item in lst:
        assert isinstance(item, dict)
        assert set(item.keys()) & set(DETAIL_PROPERTIES) == set()


def test_get_blocks_by_rids_with_detail(client_without_auth):
    res = client_without_auth.block.get_by_rids(VALID_BLOCKS, with_detail=True)
    assert res.status_code == 200
    lst = res.json()
    assert isinstance(lst, list)
    for item in lst:
        assert isinstance(item, dict)
        assert (
            set(item.keys()) & set(DETAIL_PROPERTIES) == set(DETAIL_PROPERTIES)
        )
