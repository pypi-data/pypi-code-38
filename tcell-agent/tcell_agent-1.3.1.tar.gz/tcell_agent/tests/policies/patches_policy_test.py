import unittest

from tcell_agent.policies.patches_policy import PatchesPolicy
from tcell_agent.rust.native_agent import create_native_agent
from tcell_agent.tests.support.builders import ConfigurationBuilder, AppSensorMetaBuilder
from tcell_agent.tests.support.free_native_agent import free_native_agent


class PatchesPolicyTest(unittest.TestCase):
    def setUp(self):
        configuration = ConfigurationBuilder().build()
        self.native_agent = create_native_agent(configuration)

    def tearDown(self):
        free_native_agent(self.native_agent.agent_ptr)

    def test_classname(self):
        self.assertEqual(PatchesPolicy.api_identifier, "patches")

    def test_enabled_ip_blocking_block_request_with_none_ip(self):
        policies_rsp = self.native_agent.update_policies({
            "patches": {
                "policy_id": "policy_id",
                "version": 2,
                "data": {
                    "rules": [{
                        "id": "blocked-ips-rule",
                        "title": "Blocked ips rule",
                        "action": "BlockIf",
                        "destinations": {"check_equals": [{"path": "*"}]},
                        "ignore": [],
                        "matches": [{
                            "all": [],
                            "any": [{
                                "ips": [{
                                    "type": "IP",
                                    "values": ["1.1.1.1"]
                                }]
                            }]
                        }]
                    }]
                }
            }
        })

        policy = PatchesPolicy(self.native_agent, policies_rsp["enablements"], None)
        appsensor_meta = AppSensorMetaBuilder().update_attribute(
            "remote_address", None
        ) .build()
        self.assertFalse(policy.block_request(appsensor_meta))

    def test_enabled_ip_blocking_block_request_with_empty_ip(self):
        policies_rsp = self.native_agent.update_policies({
            "patches": {
                "policy_id": "policy_id",
                "version": 2,
                "data": {
                    "rules": [{
                        "id": "blocked-ips-rule",
                        "title": "Blocked ips rule",
                        "action": "BlockIf",
                        "destinations": {"check_equals": [{"path": "*"}]},
                        "ignore": [],
                        "matches": [{
                            "all": [],
                            "any": [{
                                "ips": [{
                                    "type": "IP",
                                    "values": ["1.1.1.1"]
                                }]
                            }]
                        }]
                    }]
                }
            }
        })

        policy = PatchesPolicy(self.native_agent, policies_rsp["enablements"], None)
        appsensor_meta = AppSensorMetaBuilder().update_attribute(
            "remote_address", ""
        ) .build()
        self.assertFalse(policy.block_request(appsensor_meta))

    def test_enabled_ip_blocking_block_request_with_blocked_ip(self):
        policies_rsp = self.native_agent.update_policies({
            "patches": {
                "policy_id": "policy_id",
                "version": 2,
                "data": {
                    "rules": [{
                        "id": "blocked-ips-rule",
                        "title": "Blocked ips rule",
                        "action": "BlockIf",
                        "destinations": {"check_equals": [{"path": "*"}]},
                        "ignore": [],
                        "matches": [{
                            "all": [],
                            "any": [{
                                "ips": [{
                                    "type": "IP",
                                    "values": ["1.1.1.1"]
                                }]
                            }]
                        }]
                    }]
                }
            }
        })

        policy = PatchesPolicy(self.native_agent, policies_rsp["enablements"], None)
        appsensor_meta = AppSensorMetaBuilder().update_attribute(
            "remote_address", "1.1.1.1"
        ) .build()
        self.assertTrue(policy.block_request(appsensor_meta))

    def test_enabled_ip_blocking_block_request_with_non_blocked_ip(self):
        policies_rsp = self.native_agent.update_policies({
            "patches": {
                "policy_id": "policy_id",
                "version": 2,
                "data": {
                    "rules": [{
                        "id": "blocked-ips-rule",
                        "title": "Blocked ips rule",
                        "action": "BlockIf",
                        "destinations": {"check_equals": [{"path": "*"}]},
                        "ignore": [],
                        "matches": [{
                            "all": [],
                            "any": [{
                                "ips": [{
                                    "type": "IP",
                                    "values": ["1.1.1.1"]
                                }]
                            }]
                        }]
                    }]
                }
            }
        })

        policy = PatchesPolicy(self.native_agent, policies_rsp["enablements"], None)
        appsensor_meta = AppSensorMetaBuilder().update_attribute(
            "remote_address", "2.2.2.2"
        ) .build()
        self.assertFalse(policy.block_request(appsensor_meta))
