# -*- coding: utf-8 -*-
'''
main-файл для извлечения признаков
'''

from MarkupCorpus import *

def extractFeatures():
	'''
	Извлекаем признаки
	'''
	inputDir = "C:\\development\\OpenCorpora\\FactExtAutoAssesst\\data\\factRuEval-2016-master\\factRuEval-2016-master\\devset"
	corpus = MarkupCorpus(inputDir)
	for doc in corpus:
		pass

if __name__ == '__main__':
	extractFeatures()
