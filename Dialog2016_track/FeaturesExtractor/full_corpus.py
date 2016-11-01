# -*- coding: utf-8 -*-

import collections
import id_generator
import markup_doc
import os
from markup_doc import TokenInfo

DOCUMENTS_CHUNK_SIZE = 100

class TokenizedDocument:
	def __init__(self, input_dir, document_name):
		# Читаем текст документа.
		full_name = os.path.join(input_dir, document_name)
		with open(full_name + ".txt", encoding = "utf-8") as text_file:
			document_text = text_file.read()
		# Читаем токены и находим их в тексте
		text_pos = 0
		self.tokens = {}
		with open(full_name + ".txt.tokens", encoding = "utf-8") as token_file:
			for file_line in token_file.readlines():
				token_text = file_line.replace("\n", "")
				if not token_text:
					continue
				while not TokenizedDocument.is_matched(document_text, text_pos, token_text):
					text_pos += 1
				token_id = id_generator.IdGenerator.get()
				token = markup_doc.TokenInfo(token_id, text_pos, len(token_text), token_text)
				self.tokens[token_id] = token
				text_pos += 1
	@staticmethod
	def is_matched(document_text, text_pos, token_text):
		# Пытаемся оптимизировать вместо встроенных функций
		# TODO: нужно ли так делать?
		for (ch, pos) in zip(token_text, range(len(token_text))):
			if token_text[pos] != document_text[text_pos + pos]:
				return False
		return True

class FullCorpus:
	''' "Полный" корпус. 
	TODO: комментарий
	'''
	
	def __init__(self, input_dir):
		self.current_doc_pos = 0
		self.input_dir = input_dir
		
		# Оставляем только файлы, имя которых начинается с "book_".
		dir_file_names = filter(lambda x: x.find("book_") == 0, os.listdir(input_dir))
		
		# Убираем расширения файлов.
		doc_names = map(lambda x: x[0:x.find(".")], dir_file_names)
		
		# оставляем только документы с полной информацией, 
		# то есть для каждого документа book_id есть:
		# txt.tokens-файл и txt-файл (всего 2 штуки)
		cnt = collections.Counter(doc_names)
		self.document_list = list(filter(lambda x: cnt[x] == 2, cnt))
		self.document_list.sort()
	def get_documents_chunk(self):
		''' Получаем очередную порцию документов. 
		Порция содержит DOCUMENTS_CHUNK_SIZE или меньше документов.
		Возвращаем True, если еще есть документы (итерация продолжается).
		Если итерация завершена, то возвращаем False.
		'''
		сhunk_size = min(DOCUMENTS_CHUNK_SIZE, len(self.document_list) - self.current_doc_pos)
		if сhunk_size == 0:
			return []
		
		# TODO: id token'ов -> имена документов
		result = self.document_list[self.current_doc_pos:self.current_doc_pos+сhunk_size]
		self.current_doc_pos += сhunk_size
		return result
	def get_document_info(self, document_name):
		return TokenizedDocument(self.input_dir, document_name)
