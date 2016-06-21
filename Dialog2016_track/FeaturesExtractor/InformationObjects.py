# -*- coding: utf-8 -*-
import functools

class InformationObjects(object):
	''' Набор информационных объектов для токена. Используется в нескольких местах, поэтому логика вынесена отдельно.'''
	# TODO: можно ли это изящнее сделать? Через пропертки и дескрипторы криво вышло, поэтому просто класс.
	def __init__(self):
		self.objects = set()
	def get(self):
		if (not self.objects):
			return "NONE"
		return functools.reduce(lambda x,y : x + "+" + y, self.objects)
	def addObject(self, obj):
		assert isinstance(obj, str)
		self.objects.add(obj)
