from tcell_agent.global_state import set_agent_has_started
set_agent_has_started()

from tcell_agent.global_state import enable_test_mode
enable_test_mode()

from tcell_agent.routes.routes_sender import set_route_table_has_been_sent
set_route_table_has_been_sent()

from tcell_agent.rust.native_library import load_native_lib
load_native_lib()
