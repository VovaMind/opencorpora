# -*- coding: utf-8 -*-

import os
from FirstTrackOutput import FirstTrackOutput

class ParticipantOutput(object):
	def __init__(self, outputDir, name):
		self.outputDir = outputDir
		self.name = name
		# Участники сдавали в разных форматах. Часто результаты лежат во внутренних папках.
		while True:
			dirContent = os.listdir(self.outputDir)
			# если внтури есть файлы (не каталоги), то останавливаемся
			needStop = False
			for fileName in dirContent:
				if not os.path.isdir(os.path.join(self.outputDir, fileName)):
					needStop = True
					break
			if needStop:
				self.dirContent = set(map(lambda x: os.path.join(self.outputDir, x), dirContent))
				break
			# если внутри есть каталоги, то только один. Иначе не знаем куда спускаться
			# TODO: тут есть исключения, нужно их внимательно смотреть
			assert len(dirContent) == 1
			self.outputDir = os.path.join(self.outputDir, dirContent[0])
	def getOutputFileName(self, fileName, trackId):
		''' Формируем имя файла с результатами для пары (файл, номер_дорожки). '''
		return os.path.join(self.outputDir, fileName) + ".task" + str(trackId)
	def hasOutput(self, fileName, trackId):
		''' Проверяем наличие результата для пары (файл, номер_дорожки). '''
		#return os.path.isfile(self.getOutputFileName(fileName, trackId))
		return self.getOutputFileName(fileName, trackId) in self.dirContent
	def getTrackOutput(self, fileName, trackId):
		''' Получаем результат участника для пары (файл, номер_дорожки). '''
		assert trackId in (1,2,3) # Нам нужны только дорожки 1,2,3
		assert trackId == 1 # Временное ограничение, пока нас интересует только дорожка 1
		if (trackId == 1):
			return FirstTrackOutput(self.getOutputFileName(fileName, trackId))
