# -*- coding: utf-8 -*-

from ParticipantSets import ParticipantSets
from MarkupCorpus import MarkupCorpus
import bisect
from pandas import DataFrame, options
from InformationObjects import *

class FeaturesExtractor(object):
	@staticmethod
	def createInitDataFrame(docTokens, participantOutputs):
		''' Создаем и инициализируем DataFrame. Строки - токены, столбцы - признаки '''
		initData = {'token_id' : [], 'token_text' : [], 'token_objects' : [], 'token_type' : []}
		for token in docTokens:
			initData['token_id'].append(token.id)
			initData['token_text'].append(token.text)
			initData['token_objects'].append(token.objTypes.get())
			initData['token_type'].append(token.type)
		for participant in participantOutputs:
			initData[FeaturesExtractor.getParticipantColName(participant.name)] = []
			for i in range(len(docTokens)):
				initData[FeaturesExtractor.getParticipantColName(participant.name)].append(InformationObjects())
		return initData
	@staticmethod
	def prepareForOutput(resultData):
		''' Заменяем объекты InformationObjects на строковые представления. '''
		data = DataFrame.from_dict(resultData)
		for colName in data.columns:
			colomnValues = data[colName]
			isChecked = False
			updValues = []
			for value in colomnValues:
				if not isChecked:
					if isinstance(value, InformationObjects):
						isChecked = True
					else:
						break
				updValues.append(value.get())
			if updValues:
				data[colName] = updValues
		return data
	@staticmethod
	def getParticipantColName(participantName):
		''' Получаем имя столбца DataFramе для результатов одного из участников. '''
		result = str(participantName)
		dotPos = participantName.find('.')
		if dotPos != -1:
			result = result[0:dotPos]
		return result + "_result"
	@staticmethod
	def extractMarkupData_track1(markupDir, participantsDir, outputFileName):
		''' Извлекаем данные для размеченного корпуса (дорожка 1). '''
		# Загружаем результаты участников для размеченного корпуса
		sets = ParticipantSets(participantsDir)
		devSets = sets.getTypedSets("dev")
		# Загружаем объекты ParticipantOutput только один раз, так как работа с файловой системой медленная
		participantOutputs = []
		for devSet in devSets:
			participantOutputs.append(devSet)
		# Загружаем сам корпус
		corpus = MarkupCorpus(markupDir)
		hasHeader = True # добавляем ли заголовок 
		for doc in corpus:
			print(doc.fileName)
			# Копируем информацию о токенах документа
			docTokens = list(doc.tokens.values())
			tokensStartPos = list(map(lambda x: x.pos, docTokens))
			docTokens.sort(key = lambda x: x.pos)
			tokensStartPos.sort()
			# Создаем DataFrame
			resultData = FeaturesExtractor.createInitDataFrame(docTokens, participantOutputs)
			# Итерируем участников и навешиваем объекты на токены
			for participant in participantOutputs:
				columnName = FeaturesExtractor.getParticipantColName(participant.name)
				if participant.hasOutput(doc.fileName, trackId = 1):
					foundObjects = participant.getTrackOutput(doc.fileName, trackId = 1).getFoundObjects()
					for obj in foundObjects:
						tokenId = bisect.bisect_left(tokensStartPos, obj.pos)
						while tokenId < len(docTokens) and obj.pos + obj.length >= docTokens[tokenId].pos:
							# Проверяем пересечение границ токенов
							if (max(obj.pos, docTokens[tokenId].pos) < 
							min(obj.pos + obj.length, docTokens[tokenId].pos + docTokens[tokenId].length)):
								resultData[columnName][tokenId].addObject(obj.type)
							tokenId += 1
				else:
					for value in resultData[columnName]:
						value.addObject('UNKNOWN')
			# Выводим данные
			outputData = FeaturesExtractor.prepareForOutput(resultData)
			with open(outputFileName, 'a', encoding='utf8') as outputFile:
				outputFile.write(outputData.to_csv(index = False, header = hasHeader))
			hasHeader = False
