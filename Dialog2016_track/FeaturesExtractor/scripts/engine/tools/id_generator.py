# -*- coding: utf-8 -*-

class IdGenerator:
	def __init__(self, start_id = 0):
		self.current_id = start_id
	def get(self):
		self.current_id += 1
		return self.current_id
