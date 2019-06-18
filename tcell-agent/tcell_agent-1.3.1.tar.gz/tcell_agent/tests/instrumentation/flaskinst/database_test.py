import sys

# features from py 3.0 are used in order to set up the tests properly
if sys.version_info >= (3, 0):
    import unittest

    from types import ModuleType
    from mock import Mock, patch

    from tcell_agent.agent import TCellAgent
    from tcell_agent.policies.policy_types import PolicyTypes
    from tcell_agent.appsensor.meta import AppSensorMeta
    from tcell_agent.instrumentation.flaskinst.database import check_database_errors

    class DatabaseError(object):
        pass

    class OperationalError(DatabaseError):
        pass

    class SomeOtherError(object):
        pass

    sqlalchemy = ModuleType("sqlalchemy")
    exc = ModuleType("exc")

    class DatabaseTest(unittest.TestCase):

        @classmethod
        def setUpClass(cls):
            sqlalchemy.__file__ = sqlalchemy.__name__ + ".py"  # pylint: disable=no-member
            sqlalchemy.__path__ = []
            sys.modules[sqlalchemy.__name__] = sqlalchemy  # pylint: disable=no-member

            exc.__file__ = exc.__name__ + ".py"  # pylint: disable=no-member
            sys.modules["sqlalchemy.exc"] = exc

            setattr(exc, "DatabaseError", DatabaseError)
            setattr(exc, "OperationalError", OperationalError)

        def test_rust_policies_disabled_appfirewall_check_database_errors(self):
            request = Mock(_appsensor_meta=AppSensorMeta())
            tb = Mock(tb_fram=["trace", "stack"])
            rust_policies = Mock(appfirewall_enabled=False)

            with patch.object(TCellAgent, "get_policy", return_value=rust_policies) as patched_get_policy:
                with patch("traceback.format_tb", return_value=["trace", "stack"]) as patched_format_tb:
                    check_database_errors(request, OperationalError, tb)

                    patched_get_policy.assert_called_once_with(PolicyTypes.APPSENSOR)
                    self.assertTrue(patched_get_policy.called)
                    self.assertFalse(patched_format_tb.called)
                    self.assertEqual(request._appsensor_meta.sql_exceptions, [])

        def test_appsensor_policy_with_someothererror_check_database_errors(self):
            request = Mock(_appsensor_meta=AppSensorMeta())
            tb = Mock(tb_fram=["trace", "stack"])
            rust_policies = Mock(appfirewall_enabled=True)

            with patch.object(TCellAgent, "get_policy", return_value=rust_policies) as patched_get_policy:
                with patch("traceback.format_tb", return_value=["trace", "stack"]) as patched_format_tb:
                    check_database_errors(request, SomeOtherError, tb)

                    patched_get_policy.assert_called_once_with(PolicyTypes.APPSENSOR)
                    self.assertTrue(patched_get_policy.called)
                    self.assertFalse(patched_format_tb.called)
                    self.assertEqual(request._appsensor_meta.sql_exceptions, [])

        def test_rust_policies_with_operationerror_check_database_errors(self):
            request = Mock(_appsensor_meta=AppSensorMeta())
            tb = Mock(tb_fram=["trace", "stack"])
            rust_policies = Mock(appfirewall_enabled=True)

            with patch.object(TCellAgent, "get_policy", return_value=rust_policies) as patched_get_policy:
                with patch("traceback.format_tb", return_value=["trace", "stack"]) as patched_format_tb:
                    check_database_errors(request, OperationalError, tb)

                    patched_get_policy.assert_called_once_with(PolicyTypes.APPSENSOR)
                    self.assertTrue(patched_get_policy.called)
                    self.assertTrue(patched_format_tb.called)
                    self.assertEqual(request._appsensor_meta.sql_exceptions,
                                     [{"exception_name": "OperationalError",
                                       "exception_payload": "stacktrace"}])
