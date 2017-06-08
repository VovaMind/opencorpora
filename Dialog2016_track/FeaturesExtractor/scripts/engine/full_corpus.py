# -*- coding: utf-8 -*-

from markup_doc import TokenInfo
from common_config import DOCUMENTS_CHUNK_SIZE, GET_CORPORA_FEATURES_PARAMS

import markup_doc
import os

class TokenizedDocument:
	def __init__(self, text_file_name, token_file_name, id_generator):
		with open(text_file_name, encoding = "utf-8") as text_file:
			document_text = text_file.read()
		# Читаем токены и находим их в тексте
		text_pos = 0
		self.tokens = {}
		with open(token_file_name, encoding = "utf-8") as token_file:
			for file_line in token_file.readlines():
				token_text = file_line.replace("\n", "")
				if not token_text:
					continue
				while not TokenizedDocument.is_matched(document_text, text_pos, token_text):
					text_pos += 1
				token_id = id_generator.get()
				token = markup_doc.TokenInfo(token_id, text_pos, len(token_text), token_text)
				self.tokens[token_id] = token
				text_pos += len(token_text)
	# TODO: велосипед?
	@staticmethod
	def is_matched(document_text, text_pos, token_text):
		for pos in range(len(token_text)):
			if token_text[pos] != document_text[text_pos + pos]:
				return False
		return True

class FullCorpus:
	''' "Полный" корпус для разметки. Содержит только тексты и токенизацию.
	Читаем только документы, где ID % parts_count == part_id'''
	def __init__(self, documents_list, chunk_size, parts_count, part_id, id_generator):
		self.documents_cache = {}
		self.documents_info = {} # document id -> (text_file, tokens_file)
		self.documents_list = documents_list
		self.chunk_size = chunk_size
		self.parts_count = parts_count
		self.part_id = part_id
		self.id_generator = id_generator
	def document_chunks(self):
		''' Итерация порций документов. Порция содержит не более self.chunk_size документов.
		'''
		current_chunk = []
		for doc_info in self.documents_list.load():
			if doc_info["info#id"] % self.parts_count != self.part_id:
				continue
			self.documents_info[doc_info["info#id"]] = doc_info
			current_chunk.append(doc_info["info#id"])
			if len(current_chunk) == self.chunk_size:
				yield current_chunk
				current_chunk = []
		if current_chunk:
			yield current_chunk
	def get_document(self, document_id):
		# Хотим при нескольких обращениях к одному и тому же документу получать
		# одинаковые номера токенов. Для этого используем кэш.
		if (document_id not in self.documents_cache):
			self.documents_cache[document_id] = TokenizedDocument(
				self.documents_info[document_id]["info#text"], 
				self.documents_info[document_id]["info#tokenization"],
				self.id_generator)
		return self.documents_cache[document_id]
	def get_document_info(self, document_id):
		return self.documents_info[document_id]
	def clear_documents_cache(self):
		self.documents_cache = {}
		self.documents_info = {}
