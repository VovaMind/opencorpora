# -*- coding: utf-8 -*-

import collections
import markup_doc
import os

class MarkupCorpus:
	'''Размеченный корпус. 
	По сути это итератор размеченных документов.
	'''
	
	def __init__(self, input_dir):
		self.input_dir = input_dir
		
		# Оставляем только файлы, имя которых начинается с "book_".
		dir_file_names = filter(lambda x: x.find("book_") == 0, os.listdir(input_dir))
		
		# Убираем расширения файлов.
		doc_names = map(lambda x: x[0:x.find(".")], dir_file_names)
		
		# оставляем только документы с полной информацией, 
		# то есть для каждого документа book_id есть:
		# coref-файл, facts-файл, objects-файл, spans-файл, 
		# tokens-файл и txt-файл (всего 6 штук)
		cnt = collections.Counter(doc_names)
		self.document_list = list(filter(lambda x: cnt[x] == 6, cnt))
	
	# TODO: схема с doc_index выглядит велосипедно немного, 
	# подумать как улучшить
	def __iter__(self):
		self.doc_index = -1
		return self
	
	def __next__(self):
		if self.doc_index + 1 < len(self.document_list):
			self.doc_index += 1
			return markup_doc.MarkupDoc(
				os.path.join(self.input_dir, self.document_list[self.doc_index]), 
				self.document_list[self.doc_index])
		else:
			raise StopIteration()
