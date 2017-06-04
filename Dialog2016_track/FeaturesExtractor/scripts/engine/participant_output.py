# -*- coding: utf-8 -*-

from first_track_output import FirstTrackOutput

import os

class ParticipantOutput(object):
	def __init__(self, name, doc_info):
		self.name = name
		self.doc_info = dict(doc_info)
	def has_output(self, doc_id):
		'''Проверяем наличие результата для пары:
		(файл, номер_дорожки).
		'''
		return doc_id in self.doc_info
	def get_track_output(self, track_id, doc_id):
		'''Получаем результат участника для пары:
		(файл, номер_дорожки).
		'''
		assert track_id == 1 
		return FirstTrackOutput(self.doc_info[doc_id])
