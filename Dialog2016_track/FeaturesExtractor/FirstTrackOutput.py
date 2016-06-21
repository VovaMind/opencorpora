# -*- coding: utf-8 -*-

import os
import re
import functools

class FoundObject(object):
	def __init__(self, type, pos, length):
		self.type = type
		self.pos = pos
		self.length = length

class FirstTrackOutput(object):
	def __init__ (self, fileName):
		self.foundObjects = []
		with open(fileName, encoding = "utf-8") as resultFile:
			for fileLine in resultFile.readlines():
				line = filter(lambda ch: ch.isalnum() or ch in [' ', '\t'], fileLine)
				line = functools.reduce(lambda x, y: x + y, line)
				parts = re.split(" |\t", line.replace("\n", "").upper())
				assert len(parts) == 3
				self.foundObjects.append(FoundObject(type = parts[0], pos = int(parts[1]), length = int(parts[2])))
		pass
	# Нужен ли этот метод?
	def getFoundObjects(self):
		''' Получение найденных в документе объектов. '''
		return self.foundObjects
