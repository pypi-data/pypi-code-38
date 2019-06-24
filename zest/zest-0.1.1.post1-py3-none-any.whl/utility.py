def raises(error, function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except error:
        return True
    except:
        pass
    return False