# -*- coding: utf-8 -*-
import pickle
import string_set

class SetsCollection(object):
	''' Коллекция StringSet разбитая по lable'ам. '''
	def __init__(self):
		self.labeled_sets = {}
	def add_set(self, label, value):
		if label not in self.labeled_sets:
			self.labeled_sets[label] = set()
		self.labeled_sets[label].add(value)
	def has_set(self, label, value):
		if label not in self.labeled_sets:
			print("UNKNOWN LABEL: " + label)
			return False
		return value in self.labeled_sets[label]
	def find_closest_set(self, label, value):
		''' Находим множество с наибольшим совпадением. '''
		input_set = string_set.StringSet()
		input_set.load_from_string(value)
		best_match = -1
		best_set = string_set.StringSet()
		for current_set_str in sorted(self.labeled_sets[label]):
			current_set = string_set.StringSet()
			current_set.load_from_string(current_set_str)
			current_match = input_set.get_match(current_set)
			if current_match > best_match:
				best_match = current_match
				best_set = current_set
		return best_set.get_all()
	def save(self, file_name):
		pickle.dump(self.labeled_sets, open(file_name, "wb"))
	def load(self, file_name):
		self.labeled_sets = pickle.load(open(file_name, "rb"))
