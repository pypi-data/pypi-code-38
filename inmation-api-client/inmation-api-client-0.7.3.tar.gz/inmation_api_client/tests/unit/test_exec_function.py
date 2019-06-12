import unittest

from inmation_api_client.model import Item
from .base import TestBase


class TestExecFunction(TestBase):
    def setUp(self):
        self.context = Item(self.core_path)
        self.script = """inmation.setvalue("/System/Core.ScriptLibrary.LuaModuleName", {"MathLib2"})
        inmation.setvalue("/System/Core.ScriptLibrary.AdvancedLuaScript", {[[MathLib = {
            Pi = function()
                return 3.14
            end,
            Multiply = function(a,b)
                return a * b
            end
        }
        return MathLib]]})

        inmation.setvalue("/System/Core.ScriptLibrary.LuaModuleMandatoryExecution", {0})
        """
        self.client.RunScript(self.context, self.script)

    def test_can_execute_function_no_args(self):
        res = self.client.ExecuteFunction(self.context, 'MathLib2', 'Pi')
        self.assertEqual(res['code'], 200)
        self.assertNotIn('error', res.keys())
        self.assertEqual(res['data'][0]['v'], 3.14)

    @unittest.skip
    def test_can_execute_function_with_args(self):
        res = self.client.ExecuteFunction(self.context, 'MathLib2', 'Multiply', {'a': 2, 'b': 4})
        self.assertEqual(res['code'], 200)
        self.assertNotIn('error', res.keys())
        self.assertEqual(res['data'][0]['v'], 8)

    def test_can_exec_function_async(self):
        res = self.run_coro(self.client.ExecuteFunctionAsync(self.context, 'MathLib2', 'Pi'))
        self.assertEqual(res['code'], 200)
        self.assertNotIn('error', res.keys())
        self.assertEqual(res['data'][0]['v'], 3.14)
