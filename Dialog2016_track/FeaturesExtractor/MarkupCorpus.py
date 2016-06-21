# -*- coding: utf-8 -*-

import os
import collections
from MarkupDoc import *

class MarkupCorpus:
	'''
	Размеченный корпус. По сути это итератор размеченных документов.
	'''
	
	def __init__(self, inputDir):
		self.inputDir = inputDir
		
		# оставляем только файлы, имя которых начинается с "book_"
		dirFileNames = filter(lambda x: x.find("book_") == 0, os.listdir(inputDir))
		
		# убираем расширения файлов, 
		docNames = map(lambda x: x[0:x.find(".")], dirFileNames)
		
		# оставляем только документы с полной информацией, то есть для каждого документа book_id есть:
		# coref-файл, facts-файл, objects-файл, spans-файл, tokens-файл и txt-файл (6 штук)
		cnt = collections.Counter(docNames)
		self.documentList = list(filter(lambda x: cnt[x] == 6, cnt))
	
	# TODO: схема с docIndex выглядит велосипедно немного, подумать как улучшить
	def __iter__(self):
		self.docIndex = -1
		return self
	
	def __next__(self):
		if self.docIndex + 1 < len(self.documentList):
			self.docIndex += 1
			return MarkupDoc(os.path.join(self.inputDir, self.documentList[self.docIndex]), self.documentList[self.docIndex])
		else:
			raise StopIteration()
			