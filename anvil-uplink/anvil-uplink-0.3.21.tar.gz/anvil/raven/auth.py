import anvil.server

def get_user_crsid():
    return anvil.server.call("anvil.private.raven.get_user_crsid")

def get_user_email():
    return anvil.server.call("anvil.private.raven.get_user_email")
