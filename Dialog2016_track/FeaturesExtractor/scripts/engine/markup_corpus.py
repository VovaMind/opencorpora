# -*- coding: utf-8 -*-

import collections
import markup_doc
import os

class MarkupCorpus:
	'''Размеченный корпус. 
	По сути это итератор размеченных документов.
	'''
	def __init__(self, documents_list):
		self.documents_list = documents_list
		self.distinguish_span_begin = False
		self.distinguish_object_begin = False
	def load_documents(self):
		for doc_info in self.documents_list.load():
			yield markup_doc.MarkupDoc(doc_info, False, self.distinguish_span_begin,
				self.distinguish_object_begin)
