import re


def sanitize_dataset_uid(uid = ''):
	suggested = uid.lower()
	suggested = suggested.replace('_', '-')
	suggested = re.sub('[^A-Za-z0-9\-]+', '', suggested)
	# Do not allow uid to start with a non-alphanumeric
	# End must also be alphanumeric
	# todo verify strip operations
	suggested = suggested.strip('-')
	if len(suggested) > 25:
		suggested = suggested[0:25]
	if len(suggested) < 3:
		suggested = suggested.zfill(3)
	return suggested
