import os
import re
import bisect
from InformationObjects import *

class TokenInfo(object):
	'''
	Информация о конкретном токене из документа
	'''
	def __init__(self, id, pos, length, text):
		self.id = id
		self.pos = pos
		self.length = length
		self.text = text
		self.determineTokenType()
		self.objTypes = InformationObjects()
		
	def determineTokenType(self):
		'''
		Определяем тип токена. Пока что отличаем пунктуаторы(точки, запятые, кавычки и т.д.) и обычные токены.
		'''
		self.type = "Punctuator"
		# Если есть хотя бы один алфавитный символ, то считаем токен словом
		if re.search(r"\w", self.text) is not None:
			self.type = "Word"

class SpanInfo(object):
	'''
	Информация о конкретном спане из документа
	'''
	def __init__(self, type, id, textPos, textLength, tokenPos, tokenLength):
		self.type = type
		self.id = id
		self.textPos = textPos
		self.textLength = textLength
		self.tokenPos = tokenPos
		self.tokenLength = tokenLength

class ObjectInfo(object):
	'''
	Информация о конкретном объекте из документа
	'''
	def __init__(self, id, type, spanIds):
		self.id = id
		self.type = type
		self.spanIds = spanIds

class MarkupDoc(object):
	'''
	Размеченный документ
	'''
	def __init__(self, docName, fileName):
		# Полный путь к документу. 
		# Например, "D:\vova\boch_2016\factRuEval-2016-master\factRuEval-2016-master\devset\book_58".
		self.docName = docName 
		self.fileName = fileName # Само название документа. Например "book_58".
		
		# Извлекаем токены.
		self.extractTokens()
		
		# Извлекаем спаны.
		self.extractSpans()
		
		# Извлекаем объекты.
		self.extractObjects()
		
		# Навешиваем объекты на токены.
		self.hangObjects()
		
	def extractTokens(self):
		'''
		Извлечение токенов.
		'''
		self.tokens = {}
		with open(self.docName + ".tokens", encoding = "utf-8") as tokenFile:
			for fileLine in tokenFile.readlines():
				# Формат информации о токене следующий: id начальная_позиция длина текст
				# Например, "143784 2 11 понедельник".
				parts = fileLine.replace("\n", "").split(" ")
				
				# В tokens-файле предложения разделены пустыми строками. 
				# Пропускаем их, так как нас пока не интересуют границы предложений.
				if (len(parts) < 4):
					continue
				tokenId = int(parts[0])
				self.tokens[tokenId] = TokenInfo(id = tokenId, pos = int(parts[1]), length = int(parts[2]), 
				text = parts[3])
	
	def extractSpans(self):
		'''
		Извлечение спанов.
		'''
		self.spans = {}
		with open(self.docName + ".spans", encoding = "utf-8") as spanFile:
			for fileLine in spanFile.readlines():
				# Формат информации о спане следующий: 
				# id тип_спана позиция_в_тексте длина_в_тексте позиция_в_спанах длина_в_спанах # доп_инфа
				# Например, "22827 surname 62 7 149391 1  # 149391 Кемпинг".
				parts = fileLine[0:fileLine.find("#")].replace("\n", "").strip().split(" ")
				assert len(parts) == 6
				
				spanId = int(parts[0])
				self.spans[spanId] = SpanInfo(id = spanId, type = parts[1], textPos = int(parts[2]), 
				textLength = int(parts[3]), tokenPos = int(parts[4]), tokenLength = int(parts[5]))
	
	def extractObjects(self):
		'''
		Извлечение объектов.
		'''
		self.objects = {}
		with open(self.docName + ".objects", encoding = "utf-8") as objectFile:
			for fileLine in objectFile.readlines():
				# Формат информации о спане следующий: 
				# id тип_объекта id_спанов # доп_инфа
				# Например, "10443 Location 22782 22783 22784 # Юрию Долгорукому памятника"
				parts = fileLine[0:fileLine.find("#")].replace("\n", "").strip().split(" ")
				assert len(parts) >= 3
				
				spanIds = []
				for id in range(2, len(parts)):
					spanIds.append(int(parts[id]))
				
				objId = int(parts[0])
				self.objects[objId] = ObjectInfo(id = objId, type = parts[1], spanIds = spanIds)
	
	def hangObjects(self):
		'''
		Навешиваем объекты на токены.
		'''
		# Id токенов идут с пропусками. Например, "301823, 301826, 301827" (devset\book_317).
		# Поэтому нужно их все выделять и потом работать с ними.
		tokenIds = sorted(self.tokens.keys())
		
		for objId in self.objects:
			for spanId in self.objects[objId].spanIds:
				span = self.spans[spanId]
				
				# Из-за пропусков приходится делать бин поиск.
				tokenIdPos = bisect.bisect_left(tokenIds, span.tokenPos)
				assert tokenIds[tokenIdPos] == span.tokenPos
				
				for i in range(0, span.tokenLength):
					tokenId = tokenIds[tokenIdPos + i]
					self.tokens[tokenId].objTypes.addObject(self.objects[objId].type)
