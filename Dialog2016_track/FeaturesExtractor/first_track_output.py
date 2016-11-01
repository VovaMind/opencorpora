# -*- coding: utf-8 -*-

import functools
import os
import re

class FoundObject(object):
	def __init__(self, type, pos, length):
		self.type = type
		self.pos = pos
		self.length = length

class FirstTrackOutput(object):
	def __init__(self, file_name):
		self.found_objects = []
		with open(file_name, encoding = "utf-8") as result_file:
			for file_line in result_file.readlines():
				temp = file_line.replace("\n", "")
				line_filter = filter(lambda ch: ch.isalnum() or ch in [' ', '\t'], temp)
				line = []
				for ch in line_filter:
					line.append(ch)
				if (len(line) < 2): # TODO: WTF
					continue
				try:
					result_line = functools.reduce(lambda x, y: x + y, line)
				except:
					continue
				parts = re.split(" |\t", result_line.upper())
				assert len(parts) == 3
				self.found_objects.append(FoundObject(type = parts[0], pos = int(parts[1]), 
					length = int(parts[2])))
	# Нужен ли этот метод?
	def getfound_objects(self):
		'''Получение найденных в документе объектов.'''
		return self.found_objects
