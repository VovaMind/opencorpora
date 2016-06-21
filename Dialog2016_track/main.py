# -*- coding: utf-8 -*-
'''
main-файл для извлечения признаков
'''

from FeaturesExtractor import *
import time

def extractFeatures():
	'''
	Извлекаем признаки
	'''
	# Путь к ручной разметке
	markupDir = "C:\\development\\OpenCorpora\\FactExtAutoAssesst\\data\\factRuEval-2016-master\\factRuEval-2016-master\\devset"
	# Путь к результатам от участников
	participantsDir = "C:\\development\\OpenCorpora\\FactExtAutoAssesst\\data\\factrueval2016"
	# Извлекаем признаки
	outputFileName = "C:\\development\\OpenCorpora\\FactExtAutoAssesst\\data\\MarkupData.csv"
	FeaturesExtractor.extractMarkupData_track1(markupDir, participantsDir, outputFileName)

if __name__ == '__main__':
	beginTime = time.time()
	extractFeatures()
	endTime = time.time()
	print("Working time: " + str(endTime-beginTime))
