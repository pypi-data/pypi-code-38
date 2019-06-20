from worker.app.modules.__init__ import Module


class DepthActivityModule(Module):
    """
    This is an abstract module that needs to be extended by actual modules.
    An example of this module would be running an app every 1 ft.
    """
    module_key = "depth_activity_module"
    collection = "depth_activity_collection"

    # override
    def process_module_state(self, state):
        state = super().process_module_state(state)

        if self.global_state.get("reset", False):
            # todo
            pass

        return state
