import unittest

from mock import Mock, patch

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.instrumentation.cmdi import should_block_shell_command, get_tcell_context
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware


class CmdiTest(unittest.TestCase):

    def test_django_no_request_get_tcell_context(self):
        with patch("tcell_agent.instrumentation.cmdi.django_active", return_value=True) as patched_django_active:
            with patch.object(GlobalRequestMiddleware, "get_current_request", return_value=None) as patched_get_current_request:
                tcell_context = get_tcell_context()

                self.assertIsNone(tcell_context)
                self.assertTrue(patched_get_current_request.called)
                self.assertTrue(patched_django_active.called)

    def test_django_with_tcell_context_get_tcell_context(self):
        context = TCellInstrumentationContext()
        request = Mock(_tcell_context=context)

        with patch("tcell_agent.instrumentation.cmdi.django_active", return_value=True) as patched_django_active:
            with patch.object(GlobalRequestMiddleware, "get_current_request", return_value=request) as patched_get_current_request:
                tcell_context = get_tcell_context()

                self.assertEqual(tcell_context, context)
                self.assertTrue(patched_get_current_request.called)
                self.assertTrue(patched_django_active.called)

    def test_none_command_should_block_shell_command(self):
        with patch("tcell_agent.instrumentation.cmdi.django_active", return_value=True) as patched_django_active:
            with patch.object(GlobalRequestMiddleware, "get_current_request", return_value=None) as patched_get_current_request:
                # assertFalse returns true if it's None which is not the same test
                self.assertEqual(should_block_shell_command(None), False)
                self.assertFalse(patched_django_active.called)
                self.assertFalse(patched_get_current_request.called)

    def test_bytes_command_should_block_shell_command(self):
        context = TCellInstrumentationContext()

        mock = Mock()
        mock.block_command = Mock(return_value=False)
        with patch("tcell_agent.instrumentation.cmdi.get_tcell_context", return_value=context) as patched_get_tcell_context:
            with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
                block_command = should_block_shell_command(b"cat passwd | grep root")
                self.assertTrue(patched_get_tcell_context.called)
                patched_get_policy.assert_called_once_with(PolicyTypes.COMMAND_INJECTION)
                mock.block_command.assert_called_once_with(b"cat passwd | grep root", context)
                self.assertEqual(block_command, False)

    def test_unicode_command_should_block_shell_command(self):
        context = TCellInstrumentationContext()

        mock = Mock()
        mock.block_command = Mock(return_value=False)
        with patch("tcell_agent.instrumentation.cmdi.get_tcell_context", return_value=context) as patched_get_tcell_context:
            with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
                block_command = should_block_shell_command(u"cat passwd | grep root")
                self.assertTrue(patched_get_tcell_context.called)
                patched_get_policy.assert_called_once_with(PolicyTypes.COMMAND_INJECTION)
                mock.block_command.assert_called_once_with(u"cat passwd | grep root", context)
                self.assertEqual(block_command, False)

    def test_string_command_should_block_shell_command(self):
        context = TCellInstrumentationContext()

        mock = Mock()
        mock.block_command = Mock(return_value=False)
        with patch("tcell_agent.instrumentation.cmdi.get_tcell_context", return_value=context) as patched_get_tcell_context:
            with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
                block_command = should_block_shell_command("cat passwd | grep root")
                self.assertTrue(patched_get_tcell_context.called)
                patched_get_policy.assert_called_once_with(PolicyTypes.COMMAND_INJECTION)
                mock.block_command.assert_called_once_with("cat passwd | grep root", context)
                self.assertEqual(block_command, False)

    def test_tuple_command_should_block_shell_command(self):
        context = TCellInstrumentationContext()

        mock = Mock()
        mock.block_command = Mock(return_value=False)
        with patch("tcell_agent.instrumentation.cmdi.get_tcell_context", return_value=context) as patched_get_tcell_context:
            with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
                block_command = should_block_shell_command(("cat", "passwd", "|", "grep", "root",))
                self.assertTrue(patched_get_tcell_context.called)
                patched_get_policy.assert_called_once_with(PolicyTypes.COMMAND_INJECTION)
                mock.block_command.assert_called_once_with("cat passwd | grep root", context)
                self.assertEqual(block_command, False)

    def test_list_command_should_block_shell_command(self):
        context = TCellInstrumentationContext()

        mock = Mock()
        mock.block_command = Mock(return_value=False)
        with patch("tcell_agent.instrumentation.cmdi.get_tcell_context", return_value=context) as patched_get_tcell_context:
            with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
                block_command = should_block_shell_command(["cat", "passwd", "|", "grep", "root"])
                self.assertTrue(patched_get_tcell_context.called)
                patched_get_policy.assert_called_once_with(PolicyTypes.COMMAND_INJECTION)
                mock.block_command.assert_called_once_with("cat passwd | grep root", context)
                self.assertEqual(block_command, False)
