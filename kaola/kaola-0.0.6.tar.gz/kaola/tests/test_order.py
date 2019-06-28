import unittest
from kaola.api.kaola import KaoLa


#
# fniki_1@163.com 密码：abc123
# appKey：edb6c3b9ac4847e7584c38e2b630b14f
# appSecret：8200ee92ec22fcae76e2f00bc5c79247188e0593
# token：bff74ff8-bbec-4699-bc4c-529801aefcb4
#

class TestOrder(unittest.TestCase):

    def test_order(self):
        """
        测试订单
        """
        kl = KaoLa("edb6c3b9ac4847e7584c38e2b630b14f", "8200ee92ec22fcae76e2f00bc5c79247188e0593",access_token="bff74ff8-bbec-4699-bc4c-529801aefcb4", sandbox=True)
        print(kl.order.search_order(
            1, 1, "2019-01-01 0:00:00", "2019-01-30 23:59:59").json())


if __name__ == "__main__":
    unittest.main()
