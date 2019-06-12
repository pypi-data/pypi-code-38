import datetime


def get_date(n_days=0):
	now = datetime.datetime.now() + datetime.timedelta(n_days)
	date = {
		'ye': str(now.year),
		'mo': str(100+now.month)[1:],
		'da': str(100+now.day)[1:],
		'ho': str(100+now.hour)[1:],
		'mi': str(100+now.minute)[1:]
	}
	return date


def get_date_ymd(n_days=0):
	date = get_date(n_days)
	return date['ye'] + date['mo'] + date['da']


def get_date_y_m_d(n_days=0):
	date = get_date(n_days)
	return date['ye'] + '-' + date['mo'] + '-' +  date['da']


def get_date_ymdhm(n_days=0):
	date = get_date(n_days)
	return date['ye'] + date['mo'] + date['da'] + '-' + date['ho'] + date['mi']