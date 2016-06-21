# -*- coding: utf-8 -*-

import os
from ParticipantOutput import *

class TypedParticipantSets(object):
	'''
	Типизированные наборы данных от участников соревнований.
	Этот класс нужен для удобной итерации.
	'''
	def __init__(self, inputDir, dirNames):
		self.inputDir = inputDir
		self.dirNames = dirNames
	# TODO: подумать как извести велосипед с self.index'ом
	def __iter__(self):
		self.index = -1;
		return self
	def __next__(self):
		self.index += 1
		if self.index < len(self.dirNames):
			return ParticipantOutput(os.path.join(self.inputDir, self.dirNames[self.index]), 
			self.dirNames[self.index])
		else:
			raise StopIteration()

class ParticipantSets(object):
	'''
	Наборы данных от участников соревнований.
	'''
	def __init__(self, inputDir):
		self.inputDir = inputDir
		# Оставляем только папки среди содержимого inputDir
		self.participantDirs = list(filter(lambda x: os.path.isdir(os.path.join(inputDir, x)), 
		os.listdir(inputDir)))
		self.dirTypes = list(map(lambda x: "" if x.find(".") == -1 else x[x.find(".") + 1 : len(x)], 
		self.participantDirs))
	
	def getTypedSets(self, type):
		return TypedParticipantSets(self.inputDir, 
		list(map(lambda x: x[0], filter(lambda x: x[1] == type, zip(self.participantDirs, self.dirTypes)))))
