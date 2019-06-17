import anvil.server

def get_client_subject_dn():
	return anvil.server.call("anvil.private.pki.get_client_subject_dn")

def get_client_email():
	return anvil.server.call("anvil.private.pki.get_client_email")