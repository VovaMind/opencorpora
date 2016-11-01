# -*- coding: utf-8 -*-

class IdGenerator:
	''' Генерация последовательных id'ков. '''
	current_id = 100000000
	@staticmethod
	def get():
		IdGenerator.current_id += 1
		return IdGenerator.current_id
