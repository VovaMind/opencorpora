# -*- coding: utf-8 -*-
import functools

class StringSet(object):
	'''Набор строк для хранения типов объектов/типов спанов для токена.
	'''
	# TODO: можно ли это изящнее сделать? 
	# Через пропертки и дескрипторы криво вышло, поэтому просто класс.
	def __init__(self):
		self.objects = set()
	def get_all(self):
		'''Выдаем весь набор строк, собранный в одну строку.
		Строки из набора разделены символом +.
		'''
		if (not self.objects):
			return "NONE"
		return functools.reduce(lambda x,y : x + "+" + y, sorted(self.objects))
	def add_string(self, obj):
		'''Добавляем строку в набор.'''
		assert isinstance(obj, str)
		self.objects.add(obj)
	def load_from_string(self, str):
		if str == "NONE":
			self.object = set()
		else:
			self.objects = set(str.split("+"))
	def get_match(self, other):
		'''Получаем число общих объектов для двух StringSet.'''
		result = 0
		for i in self.objects:
			if i in other.objects:
				result += 1
		return result
