#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import os

from Homevee.Utils.Constants import DATA_DIR


def get_image_directory_path(directory_name: str) -> str:
	"""
	Constructs the image directory path
	:param directory_name: the name of the directory
	:return: the image directory path
	"""
	path = os.path.join(DATA_DIR, "images", directory_name)
	return path

def create_image(filename: str, directory_name: str, img_data: str, optimize: bool = False) -> str:
	"""
	Creates an image
	:param filename: the filename of the image
	:param directory_name: the dirname of the image
	:param img_data: the img-data
	:param optimize: true if image should be optimized, false otherwise
	:return: the absolute path to the stored image
	"""
	filename = filename + ".jpeg"

	rel_path = os.path.join("images", directory_name)

	abs_path = os.path.join(DATA_DIR, rel_path)

	if not os.path.exists(abs_path):
		os.makedirs(abs_path)

	file_path = os.path.join(abs_path, filename)

	#Logger.log(img_data)

	img_data = base64.b64decode(img_data)

	fh = open(file_path, "wb")
	fh.write(img_data)
	fh.close()

	if(optimize):
		optimize_image(file_path)

	return os.path.join(rel_path, filename)

def optimize_image(file_path: str):
	"""
	Optimize the image
	:param file_path: path to the image
	:return:
	"""
	return