from datetime import datetime

EPOCH = 1518652800

def epoch_time(timestamp):
	return datetime.utcfromtimestamp(timestamp + EPOCH)

sentinel = object()
