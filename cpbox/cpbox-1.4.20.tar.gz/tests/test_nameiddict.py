import unittest
from cpbox.tool.datatypes import NameIdDict

class TestNameIdDict(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_all(self):
        id_1 = "r-bp194452436e8b94"
        name_1 = "yizhoucp"
        item_1 = {
                "architecture_type": "cluster",
                "bandwidth": 384,
                "capacity": 16384,
                "charge_type": "PrePaid",
                "connection_domain": "r-bp194452436e8b94.redis.rds.aliyuncs.com",
                "connections": 80000,
                "create_time": "2017-08-21T09:22:01Z",
                "end_time": "2018-10-22T16:00:00Z",
                "engine_version": "2.8",
                "has_renew_change_order": False,
                "instance_class": "redis.sharding.basic.small.default",
                "instance_id": id_1,
                "instance_name": name_1
                }

        id_2 = "r-bp1e65f4b38ae304"
        name_2 = "php-session"
        item_2 = {
                "architecture_type": "standard",
                "bandwidth": 10,
                "capacity": 1024,
                "charge_type": "PrePaid",
                "connection_domain": "php-session.redis.rds.aliyuncs.com",
                "connections": 10000,
                "create_time": "2018-09-10T09:41:01Z",
                "end_time": "2018-11-10T16:00:00Z",
                "engine_version": "4.0",
                "has_renew_change_order": False,
                "instance_class": "redis.master.small.default",
                "instance_id": id_2,
                "instance_name": name_2
                }

        data = {
                id_1: item_1,
                id_2: item_2,
                }

        name_id_dict = NameIdDict('instance_id', 'instance_name', data)
        self.assertEqual(name_id_dict[id_1], item_1)
        self.assertEqual(name_id_dict[name_1], item_1)
        self.assertEqual(name_id_dict[id_2], item_2)
        self.assertEqual(name_id_dict[name_2], item_2)
        self.assertTrue(isinstance(name_id_dict, dict))

        name_id_dict = NameIdDict('instance_id', 'instance_name')
        name_id_dict.update(data)
        self.assertEqual(name_id_dict[id_1], item_1)
        self.assertEqual(name_id_dict[name_1], item_1)
        self.assertEqual(name_id_dict[id_2], item_2)
        self.assertEqual(name_id_dict[name_2], item_2)
        self.assertTrue(isinstance(name_id_dict, dict))

if __name__ =='__main__':
    unittest.main()
