from __future__ import print_function

from tcell_agent.global_state import needs_instrumentation, set_has_been_instrumented
from tcell_agent.version import VERSION


def run_instrumentations():
    from tcell_agent.config.configuration_service import init_config
    config = init_config()
    if config.enabled and needs_instrumentation():
        set_has_been_instrumented()

        from tcell_agent.agent import TCellAgent
        TCellAgent.init_agent()

        from tcell_agent.instrumentation.djangoinst.app import instrument_django
        instrument_django()

        from tcell_agent.instrumentation.flaskinst.app import instrument_flask
        instrument_flask()

        from tcell_agent.instrumentation.hooks.login_fraud import instrument_tcell_hooks
        instrument_tcell_hooks()

        from tcell_agent.instrumentation.cmdi import instrument_commands
        instrument_commands()

        return True

    return False


def instrument():
    """
    This function could potentially be called multiple times if
    you run your application with `tcell_agent run ...` and then
    also manually call it from your wsgi.py file.

    See `tcell_agent/__init__.py` and `tcell_agent/pythonpath/sitecustomize.py`
    for more information on both ways to calling this instrumentation.

    Make sure to only instrument once.
    """
    try:
        if run_instrumentations():
            print("tCell.io Agent: [Info]  Started tCell.io agent v{version}".format(version=VERSION))
    except Exception as e:
        print(
            "tCell.io Agent: [Error] Could not start tCell.io agent v{version} {e}".format(version=VERSION,
                                                                                           e=e))
        import traceback
        traceback.print_exc()
