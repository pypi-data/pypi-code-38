__all__ = ['test']
try:
    from os_sys.programs import fail
except Exception:
    try:
        from . import fail
    except Exception:
        fail = None
fail = fail
