import bisect
import os
import re
import tools.string_set

PREPOSITIONS = ['без', 'в', 'вблизи', 'вглубь', 'вдоль', 'возле', 'вокруг', 'впереди', 'для', 
	'до', 'за', 'из', 'к', 'на', 'над', 'о', 'об', 'около', 'от', 'перед', 'по', 'под', 
	'после', 'при', 'про', 'с', 'у', 'через']

class TokenInfo(object):
	'''Информация о конкретном токене из документа'''
	def __init__(self, id, pos, length, text):
		self.id = id
		self.pos = pos
		self.length = length
		self.text = text
		self.determine_token_type()
		self.obj_types = tools.string_set.StringSet()
		self.span_types = tools.string_set.StringSet()
		
	def determine_token_type(self):
		'''Определяем тип токена. 
		Пока что отличаем пунктуаторы(точки, запятые, кавычки и т.д.) 
		и обычные токены.
		'''
		# Если есть хотя бы один алфавитный символ, 
		# то считаем токен словом
		if re.search(r"\w", self.text) is not None:
			preposition_index = bisect.bisect_left(PREPOSITIONS, self.text.lower())
			if preposition_index < len(PREPOSITIONS) and\
				PREPOSITIONS[preposition_index] == self.text.lower():
				self.type = "Preposition_" + str(preposition_index)
			else:
				self.type = "Word"
		else:
			self.type = "Punctuator:"
			# Определяем тип пунктуатора
			# TODO: 100%-й велосипед, нужно извести
			punctuator_types = {
				'.': 'Dot', 
				',' : 'Comma',
				';' : 'Semicolon',
				'?' : 'Question',
				'\'' : 'Quote',
				'"' : 'DoubleQuote',
				'!' : 'Exclamation',
				'(' : 'RoundBracketBegin',
				')' : 'RoundBracketEnd',
				'[' : 'SquareBracketBegin',
				']' : 'SquareBracketEnd',
				'{' : 'BraceBegin',
				'}' : 'BraceEnd',
				':' : 'Colon',
				'#' : 'Hashtag',
				'<' : 'Less',
				'>' : 'More',
				'-' : 'Dash'
			}
			if self.text[0] in punctuator_types:
				self.type += punctuator_types[self.text[0]]
			else:
				self.type += "Unknown"
		
class SpanInfo(object):
	'''Информация о конкретном спане из документа'''
	def __init__(self, type, id, text_pos, text_length, token_pos, token_length):
		self.type = type
		self.id = id
		self.text_pos = text_pos
		self.text_length = text_length
		self.token_pos = token_pos
		self.token_length = token_length
		self.debug_text = ""

class ObjectInfo(object):
	'''Информация о конкретном объекте из документа'''
	def __init__(self, id, type, span_ids):
		self.id = id
		self.type = type
		self.span_ids = span_ids

class MarkupDoc(object):
	'''Размеченный документ'''
	def __init__(self, doc_info, tokens_only, distinguish_span_begin, distinguish_object_begin):
		self.document_id = doc_info["info#id"]
		self.extract_tokens(doc_info["info#contest_tokenization"])
		if tokens_only:
			return 
		self.extract_spans(doc_info["info#spans"])
		self.extract_objects(doc_info["info#objects"])
		self.hang_objects(distinguish_object_begin)
		self.hang_span_types(distinguish_span_begin)
	def extract_tokens(self, file_name):
		'''Извлечение токенов.'''
		self.tokens = {}
		with open(file_name, encoding = "utf-8") as token_file:
			for file_line in token_file.readlines():
				# Формат информации о токене следующий: 
				# id начальная_позиция длина текст
				# Например, "143784 2 11 понедельник".
				parts = file_line.replace("\n", "").split(" ")
				
				# В tokens-файле предложения разделены пустыми строками.
				# Пропускаем их, так как нас пока не интересуют 
				# границы предложений.
				if (len(parts) < 4):
					continue
				token_id = int(parts[0])
				self.tokens[token_id] = TokenInfo(
					id = token_id, pos = int(parts[1]), 
					length = int(parts[2]), text = parts[3]
				)
	
	def extract_spans(self, file_name):
		'''Извлечение спанов.'''
		self.spans = {}
		with open(file_name, encoding = "utf-8") as span_file:
			for file_line in span_file.readlines():
				# Формат информации о спане следующий: 
				# id тип_спана позиция_в_тексте длина_в_тексте позиция_в_спанах длина_в_спанах # доп_инфа
				# Например, "22827 surname 62 7 149391 1  # 149391 Кемпинг".
				parts = file_line[0:file_line.find("#")].replace("\n", "").strip().split(" ")
				assert len(parts) == 6
				
				span_id = int(parts[0])
				self.spans[span_id] = SpanInfo(
					id = span_id, type = parts[1], text_pos = int(parts[2]), 
					text_length = int(parts[3]), token_pos = int(parts[4]), 
					token_length = int(parts[5])
				)
	
	def extract_objects(self, file_name):
		'''Извлечение объектов.'''
		self.objects = {}
		with open(file_name, encoding = "utf-8") as object_file:
			for file_line in object_file.readlines():
				# Формат информации о спане следующий: 
				# id тип_объекта id_спанов # доп_инфа
				# Например, "10443 Location 22782 22783 22784 # Юрию Долгорукому памятника"
				parts = file_line[0:file_line.find("#")].replace("\n", "").strip().split(" ")
				assert len(parts) >= 3
				
				span_ids = []
				for id in range(2, len(parts)):
					span_ids.append(int(parts[id]))
				
				obj_id = int(parts[0])
				self.objects[obj_id] = ObjectInfo(id = obj_id, type = parts[1], span_ids = span_ids)
	
	def hang_objects(self, distinguish_object_begin):
		'''Навешиваем объекты на токены.'''
		# Id токенов идут с пропусками. 
		# Например, "301823, 301826, 301827" (devset\book_317).
		# Поэтому нужно их все выделять и потом работать с ними.
		token_ids = sorted(self.tokens.keys())
		
		for obj_id in self.objects:
			is_first = True
			for span_id in self.objects[obj_id].span_ids:
				span = self.spans[span_id]
				
				# Из-за пропусков приходится делать бин поиск.
				token_id_pos = bisect.bisect_left(token_ids, span.token_pos)
				assert token_ids[token_id_pos] == span.token_pos
				
				for i in range(0, span.token_length):
					token_id = token_ids[token_id_pos + i]
					prefix = ""
					if distinguish_object_begin:
						prefix = "begin_"
						is_first = False
					self.tokens[token_id].obj_types.add_string(prefix + self.objects[obj_id].type)
	def hang_span_types(self, distinguish_span_begin):
		''' Навешиваем типы спанов на токены. '''
		# TODO: дублирование кода извести
		# Id токенов идут с пропусками. 
		# Например, "301823, 301826, 301827" (devset\book_317).
		# Поэтому нужно их все выделять и потом работать с ними.
		token_ids = sorted(self.tokens.keys())
		
		for span_id in self.spans:
			span = self.spans[span_id]
			is_first = True
			
			# Из-за пропусков приходится делать бин поиск.
			token_id_pos = bisect.bisect_left(token_ids, span.token_pos)
			assert token_ids[token_id_pos] == span.token_pos
			
			for i in range(0, span.token_length):
				token_id = token_ids[token_id_pos + i]
				prefix = ""
				if distinguish_span_begin and is_first:
					prefix = "begin_"
					is_first = False
				self.tokens[token_id].span_types.add_string(prefix + span.type)
