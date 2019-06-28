import os


def install(runtime="julia"):
    """Install Julia packages required for `interpretableai.iai`."""
    import julia
    os.environ['IAI_DISABLE_INIT'] = 'True'
    # TODO: pass env to pyjulia (up to 0.4.1 - will break on next release)
    julia.install(julia=runtime, env=os.environ)
    del os.environ['IAI_DISABLE_INIT']
