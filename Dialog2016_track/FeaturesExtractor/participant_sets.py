﻿# -*- coding: utf-8 -*-

import os
from participant_output import ParticipantOutput

class TypedParticipantSets(object):
	'''Типизированные наборы данных от участников соревнований.
	Этот класс нужен для удобной итерации.
	'''
	def __init__(self, input_dir, dir_names):
		self.input_dir = input_dir
		self.dir_names = dir_names
	# TODO: подумать как извести велосипед с self.index'ом
	def __iter__(self):
		self.index = -1;
		return self
	def __next__(self):
		self.index += 1
		if self.index < len(self.dir_names):
			return ParticipantOutput(os.path.join(self.input_dir, self.dir_names[self.index]), 
				self.dir_names[self.index])
		else:
			raise StopIteration()

class ParticipantSets(object):
	'''Наборы данных от участников соревнований.'''
	def __init__(self, input_dir):
		self.input_dir = input_dir
		# Оставляем только папки среди содержимого input_dir
		self.participant_dirs = list(filter(lambda x: os.path.isdir(os.path.join(input_dir, x)), 
			os.listdir(input_dir)))
		self.dirTypes = list(
			map(lambda x: "" if x.find(".") == -1 else x[x.find(".") + 1 : len(x)], 
			self.participant_dirs))
	
	def getTypedSets(self, type):
		return TypedParticipantSets(self.input_dir, 
			list(map(lambda x: x[0], filter(lambda x: x[1] == type, 
			zip(self.participant_dirs, self.dirTypes)))))