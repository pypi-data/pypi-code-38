from tcell_agent.rust.native_library import get_native_lib


def free_native_agent(agent_ptr):
    if get_native_lib():
        get_native_lib().free_agent(agent_ptr)
