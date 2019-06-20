import os
import re

from sacred import Experiment
from sacred.observers import MongoObserver
from sacred.utils import apply_backspaces_and_linefeeds

from urllib.parse import quote_plus

def progress_bar_filter(text,
	escape=re.compile(r"\x1B\[([0-?]*[ -/]*[@-~])"),
	line_contents=re.compile(r".*(total|this epoch|Estimated time|\d+ iter, \d+ epoch / \d+ epochs).*\n")):
	_text = apply_backspaces_and_linefeeds(text)
	_text = escape.sub("", _text)
	_text = line_contents.sub("", _text)
	return _text


class MyExperiment(Experiment):

	@staticmethod
	def get_creds():
		return dict(
			user=quote_plus(os.environ["MONGODB_USER_NAME"]),
			password=quote_plus(os.environ["MONGODB_PASSWORD"]),
			db_name=quote_plus(os.environ["MONGODB_DB_NAME"]),
		)

	@staticmethod
	def auth_url(creds, host="localhost", port=27017):
		url = "mongodb://{user}:{password}@{host}:{port}/{db_name}?authSource=admin".format(
			host=host, port=port, **creds)
		return url


	def __init__(self, host,
		no_observer=False,
		output_filter=progress_bar_filter,
		*args, **kwargs):
		super(MyExperiment, self).__init__(*args, **kwargs)

		self.captured_out_filter = output_filter
		if no_observer:
			return

		creds = MyExperiment.get_creds()
		self.observers.append(MongoObserver.create(
			url=MyExperiment.auth_url(creds, host=host),
			db_name=creds["db_name"]
			)
		)

	def __call__(self, args):
		self.add_config(**args.__dict__)
		return self._create_run()(args)
