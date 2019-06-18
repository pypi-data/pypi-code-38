import json

from ctypes import c_uint8

from tcell_agent.rust.native_library import get_native_lib
from tcell_agent.rust.native_agent_response import EmptyNativeAgentResponse, NativeAgentResponse
from tcell_agent.utils.compat import to_bytes


class NativeCaller(object):
    def __init__(self, native_method_name, bytes_to_allocate):
        self.native_method_name = native_method_name
        buf_type = c_uint8 * bytes_to_allocate
        self.response = buf_type()  # allocate memory
        self.args = ()

    def append_parameter(self, message):
        message_bytes = to_bytes(json.dumps(message))
        self.args = self.args + (message_bytes, len(message_bytes))

    def execute(self):
        if not get_native_lib():
            return EmptyNativeAgentResponse()

        args = self.args + (self.response, len(self.response),)
        response_len = getattr(get_native_lib(),
                               self.native_method_name)(*args)

        return NativeAgentResponse(self.native_method_name,
                                   self.response,
                                   response_len)


class NativeAgentCaller(NativeCaller):
    def __init__(self, agent_ptr, native_method_name, bytes_to_allocate):
        super(NativeAgentCaller, self).__init__(native_method_name,
                                                bytes_to_allocate)
        self.agent_ptr = agent_ptr
        self.args = (agent_ptr,)

    def execute(self):
        if not self.agent_ptr:
            return EmptyNativeAgentResponse()

        return super(NativeAgentCaller, self).execute()
