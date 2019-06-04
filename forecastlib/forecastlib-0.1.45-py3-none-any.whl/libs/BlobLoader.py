import json
import os
import time

import pandas as pd
from azure.storage.blob import BlockBlobService


class BlobLoader(object):
	def __init__(self, container, account, key, blob=None, local_folder=None, skip_downloads=False):
		self.container = container
		self.blob = blob
		self.account = account
		self.key = key
		self.skip_downloads = skip_downloads
		self.local_folder = local_folder

	def download(self, filename: str):
		if self.local_folder is None:
			target_path = filename
		elif self.local_folder.endswith("/"):
			target_path = self.local_folder + filename
			BlobLoader.ensure_path(target_path)

		if self.blob is not None:
			filename = self.blob + "/" + filename

		if self.skip_downloads is True:
			print("Download of %s skipped due to BlobLoader settings" % filename)
		else:
			t1 = time.time()
			blob_service = BlockBlobService(account_name=self.account, account_key=self.key)
			blob_service.get_blob_to_path(self.container, filename, target_path)
			t2 = time.time()
			print(("It takes %s seconds to download " + filename) % (t2 - t1))

		return target_path

	def load_csv(self, filename, delimiter):
		self.download(filename)
		return pd.read_csv(filename, delimiter=delimiter)

	def load_json(self, filename):
		self.download(filename)
		with open(filename) as json_file:
			return json.load(json_file)

	def load_file(self, filename):
		self.download(filename)
		with open(filename) as f:
			return f

	def load_text(self, filename):
		self.download(filename)
		with open(filename) as f:
			return f.read()

	@staticmethod
	def ensure_path(file_path):
		directory = os.path.dirname(file_path)
		if not os.path.exists(directory):
			os.makedirs(directory)
