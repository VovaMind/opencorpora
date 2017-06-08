# -*- coding: utf-8 -*-
import json

class Config(object):
	def __init__(self, file_name):
		with open(file_name) as input_file:
			self.config_data = json.load(input_file)
	def get(self, key):
		return self.config_data[key]
