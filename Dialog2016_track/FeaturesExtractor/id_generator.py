# -*- coding: utf-8 -*-

class IdGenerator:
	''' Генерация последовательных id'ков. '''
	current_id = 0
	@staticmethod
	def get():
		IdGenerator.current_id += 1
		return IdGenerator.current_id
