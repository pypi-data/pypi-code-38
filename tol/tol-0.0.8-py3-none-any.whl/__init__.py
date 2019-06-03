def get_home_dir(user):
    """
    Get user home dir
    
    NOTE: This could probably have been done nicer. Probably done this way to be able to handle
    non-standard home dir locations.
    """
    return "cd ~%s && pwd" % user
